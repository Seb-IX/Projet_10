import unittest

from config import DefaultConfig

from flight_booking_recognizer import FlightBookingRecognizer

from helpers.luis_helper_utility import predict_to_book_details
from helpers.luis_helper import Intent

# BOT FRAMEWORK
from botbuilder.dialogs.prompts import (
    PromptOptions, 
)

from botbuilder.core import (
    TurnContext, 
    ConversationState, 
    MemoryStorage, 
    MessageFactory, 
)
from botbuilder.dialogs import DialogSet, DialogTurnStatus
from botbuilder.core.adapters import TestAdapter
from botbuilder.dialogs.prompts import NumberPrompt,DateTimePrompt

import aiounittest

class TestLuisApp(unittest.TestCase):

    def test_creation_by_flight_booking_regonizer(self):
        CONFIG = DefaultConfig()

        RECOGNIZER = FlightBookingRecognizer(CONFIG)
        self.assertIsNotNone(RECOGNIZER)


    def test_utilisation_and_creation_book_details(self):
        CONFIG = DefaultConfig()
        RECOGNIZER = FlightBookingRecognizer(CONFIG)

        text = "I need book a fly From Berlin to Dublin !"
        intent,result = predict_to_book_details(RECOGNIZER.get_luis_app(),text,Intent)

        self.assertEqual(intent,Intent.BOOK_FLIGHT.value)
        self.assertIn("dublin",result.destination)
        self.assertIn("berlin",result.origin)
        self.assertIsNone(result.budget)
        self.assertIsNone(result.n_adult)
        self.assertIsNone(result.n_children)
        self.assertIsNone(result.end_date)
        self.assertIsNone(result.start_date)


class NumberPromptTest(aiounittest.AsyncTestCase):
    async def test_number_prompt(self):
        async def exec_test(turn_context:TurnContext):
            dialog_context = await dialogs.create_context(turn_context)

            results = await dialog_context.continue_dialog()
            if (results.status == DialogTurnStatus.Empty):
                options = PromptOptions(
                    prompt=MessageFactory.text("How many adults will be present?")
                )
                await dialog_context.prompt(NumberPrompt.__name__, options)

            elif results.status == DialogTurnStatus.Complete:
                reply = results.result
                await turn_context.send_activity(str(reply))

            await conv_state.save_changes(turn_context)

        adapter = TestAdapter(exec_test)

        conv_state = ConversationState(MemoryStorage())

        dialogs_state = conv_state.create_property("dialog-state")
        dialogs = DialogSet(dialogs_state)
        
        dialogs.add(NumberPrompt(NumberPrompt.__name__))

        step1 = await adapter.test('Hello', 'How many adults will be present?')
        step2 = await step1.send('Just 2 adults.')
        await step2.assert_reply("2")


    async def test_date_prompt(self):
        async def exec_test(turn_context:TurnContext):
            dialog_context = await dialogs.create_context(turn_context)

            results = await dialog_context.continue_dialog()
            if (results.status == DialogTurnStatus.Empty):
                options = PromptOptions(
                    prompt=MessageFactory.text("When you want to travel?")
                )
                await dialog_context.prompt(DateTimePrompt.__name__, options)

            elif results.status == DialogTurnStatus.Complete:
                reply = results.result
                await turn_context.send_activity(str(reply[-1].value))

            await conv_state.save_changes(turn_context)

        adapter = TestAdapter(exec_test)

        conv_state = ConversationState(MemoryStorage())

        dialogs_state = conv_state.create_property("dialog-state")
        dialogs = DialogSet(dialogs_state)
        
        dialogs.add(DateTimePrompt(DateTimePrompt.__name__))

        step1 = await adapter.test('Hello', 'When you want to travel?')
        # First test
        step2 = await step1.send('The 22 December 2022')
        await step2.assert_reply("2022-12-22")
        # Second test
        step1 = await adapter.test('Hello', 'When you want to travel?')
        step2 = await step1.send('The 25 June 2022')
        await step2.assert_reply("2022-06-25")
        

if __name__ == '__main__':
    unittest.main(module="tests")