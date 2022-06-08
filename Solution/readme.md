# Project

<p align="center">
	<img src="https://github.com/Seb-IX/Projet_10/blob/main/Solution/luis_solution/img/logo.png" style="width:400px;">
</p>

Bot script is in "bot_flyme/" directory and LUIS script is in "luis_solution/" directory.

# Architecture

<p align="center">
	<img src="https://github.com/Seb-IX/Projet_10/blob/main/Ressource/schema_architecture_gray_background.png" style="width:500px;">
</p>

# Luis app

The Luis application must be created on <a href="https://portal.azure.com/#create/Microsoft.CognitiveServicesLUISAllInOne">azure.com/luis</a> with the 2 creation options in order to have the creation / learning instance and the prediction instance usable.

Once created and trained with a script in the "/luis_solution" folder, it is possible to see the content of the different components of the LUIS modeling (Intent, Entity...) on <a href="https://luis.ai/">luis.ai</a>


# Azure bot

the bot works in 2 parts, a part that will execute the bot framework code in a <a href="https://portal.azure.com/#create/Microsoft.WebSite">WebApp</a> and an <a href="https://portal.azure.com/#create/Microsoft.AzureBot">Azure bot</a> part that will dispatch the bot to different channels (Microsft team, Skype, Web ...)
