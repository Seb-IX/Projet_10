# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions, NumberPrompt, DateTimePrompt
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from .cancel_and_help_dialog import CancelAndHelpDialog

import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler


SEVERITY_LEVEL = {
    0: "DEBUG",
    1: "INFO",
    2: "WARNING",
    3: "ERROR",
    4: "CRITICAL",
}



class BookingDialog(CancelAndHelpDialog):
    """Flight booking implementation."""

    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(BookingDialog, self).__init__(
            dialog_id or BookingDialog.__name__, telemetry_client
        )
        self.telemetry_client = telemetry_client

        
        self.logger = logging.getLogger(__name__)

        if not type(self.telemetry_client) is NullTelemetryClient:
            self.logger.addHandler(AzureLogHandler(
                connection_string=self.telemetry_client._instrumentation_key)
            )

        text_prompt = TextPrompt(TextPrompt.__name__)

        number_prompt = NumberPrompt(NumberPrompt.__name__)

        date_prompt = DateTimePrompt(DateTimePrompt.__name__)

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.destination_step,
                self.origin_step,
                self.start_date_step,
                self.end_date_step,
                self.n_adult_step,
                self.n_children_step,
                self.budget_step,
                self.seat_step,
                self.confirm_step,
                self.final_step,
            ],
        )

        self.add_dialog(text_prompt)
        self.add_dialog(number_prompt)
        self.add_dialog(date_prompt)
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))

        # waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__

        

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        booking_details = step_context.options

        if booking_details.destination is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("To what city would you like to travel?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.destination)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.destination = step_context.result
        if booking_details.origin is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("From what city will you be travelling?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.origin)

    async def start_date_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.origin = step_context.result
        if booking_details.start_date is None:
            return await step_context.prompt(
                DateTimePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("When you want to travelling?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.start_date)

    async def end_date_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.start_date = step_context.result
        if booking_details.end_date is None:
            return await step_context.prompt(
                DateTimePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("When do you want to return?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.end_date)

    async def n_adult_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.end_date = step_context.result
        if booking_details.n_adult is None:
            
            return await step_context.prompt(
                NumberPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("How many adults will be present?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.n_adult)

    async def n_children_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.n_adult = step_context.result
        if booking_details.n_children is None:
            return await step_context.prompt(
                NumberPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("How many children will be present?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.n_children)


    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        booking_details = step_context.options
        booking_details.n_children = step_context.result

        if booking_details.budget is None:
            return await step_context.prompt(
                NumberPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("What is your budget in dollars?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.budget)


    async def seat_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        booking_details = step_context.options
        booking_details.budget = step_context.result

        if booking_details.seat is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("In which class would you like to travel (business, economique...)?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        
        return await step_context.next(booking_details.seat)


    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Confirm the information the user has provided."""

        booking_details = step_context.options

        booking_details.seat = step_context.result
        # Allows you to correctly format the date entered
        if type(booking_details.start_date) is str:
            start_date = booking_details.start_date
        else:
            start_date = booking_details.start_date[-1].value

        if type(booking_details.end_date) is str:
            end_date = booking_details.end_date
        else:
            end_date = booking_details.end_date[-1].value
        msg = (
            f"Please confirm, I have you booked to {booking_details.destination} from {booking_details.origin} on {start_date} \
            to {end_date}, your budget is {booking_details.budget}$ on {booking_details.seat} seat for {booking_details.n_adult} \
            adult and {booking_details.n_children} children."
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg))
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction and end the dialog."""
        
        booking_details = step_context.options

        if step_context.result:
            self.logger.setLevel(logging.INFO)
            self.logger.info('Good answer!')
            print("Good answer")
            return await step_context.end_dialog(booking_details)

        
        if type(booking_details.start_date) is str:
            start_date = booking_details.start_date
        else:
            start_date = booking_details.start_date[-1].value

        if type(booking_details.end_date) is str:
            end_date = booking_details.end_date
        else:
            end_date = booking_details.end_date[-1].value
            
        properties = {}
        properties["Destination"] = booking_details.destination
        properties["Origin"] = booking_details.origin
        properties["Start_date"] = start_date
        properties["End_date"] = end_date
        properties["Budget"] = float(booking_details.budget)
        properties["N_adult"] = int(booking_details.n_adult)
        properties["N_children"] = int(booking_details.n_children)
        properties["Seat"] = booking_details.seat

        
        self.logger.error("Bad answer!",extra={'custom_dimensions':properties})
        print("Bad answer")

        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
