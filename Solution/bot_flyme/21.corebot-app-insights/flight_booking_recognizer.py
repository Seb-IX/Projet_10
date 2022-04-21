# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.ai.luis import LuisApplication, LuisRecognizer, LuisPredictionOptions
from luis_utility import LuisApp
from botbuilder.core import (
    Recognizer,
    RecognizerResult,
    TurnContext,
    BotTelemetryClient,
    NullTelemetryClient,
)

from config import DefaultConfig


class FlightBookingRecognizer(Recognizer):
    def __init__(
        self, configuration: DefaultConfig, telemetry_client: BotTelemetryClient = None
    ):
        self._recognizer = None

        luis_is_configured = (
            configuration.LUIS_APP_ID
            and configuration.LUIS_API_KEY
            and configuration.LUIS_API_HOST_NAME
        )
        if luis_is_configured:
            # Set the recognizer options depending on which endpoint version you want to use e.g v2 or v3.
            # More details can be found in https://docs.microsoft.com/azure/cognitive-services/luis/luis-migration-api-v3
            luis_application = LuisApplication(
                configuration.LUIS_APP_ID,
                configuration.LUIS_API_KEY,
                configuration.LUIS_API_HOST_NAME,
            )

            options = LuisPredictionOptions()
            options.telemetry_client = telemetry_client or NullTelemetryClient()

            self._recognizer = LuisRecognizer(
                luis_application, prediction_options=options
            )
            self.luis_app = LuisApp(configuration.LUIS_API_HOST_NAME,configuration.LUIS_API_KEY)
            self.luis_app.get_app(configuration.LUIS_APP_ID)

    @property
    def is_configured(self) -> bool:
        # Returns true if luis is configured in the config.py and initialized.
        return self._recognizer is not None

    async def recognize(self, turn_context: TurnContext) -> RecognizerResult:
        return await self._recognizer.recognize(turn_context)

    def get_luis_app(self):
        return self.luis_app

    def predict_turn(self,turn_context : TurnContext):
        return self.luis_app.predict(turn_context.activity.text,get_intent=True)

