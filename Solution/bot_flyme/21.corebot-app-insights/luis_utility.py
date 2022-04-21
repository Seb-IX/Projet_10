# import packages
import time
import json
from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
import requests

class LuisApp:
    def __init__(self,authoring_endpoint_luis,authoring_key_luis,
                list_entities=['dst_city','or_city','str_date','end_date','n_adult','n_children','budget','seat'],
                list_intents=['BookFlight'],
                runtime_endpoint_luis = None, runtime_key_luis = None):
        '''Permet de facilité les manipulation des application LUIS, il est bien sur nécessaire en amont de 
        créer une application LUIS sur Microsoft Azure à l'adresse suivante : 
        https://portal.azure.com/#create/Microsoft.CognitiveServicesLUISAllInOne

        Parameters:
            authoring_endpoint_luis
            authoring_key_luis
            list_entities
            list_intents
            runtime_endpoint_luis
            runtime_key_luis

        Returns:
            None

        '''
        self.AUTHORING_ENDPOINT = authoring_endpoint_luis
        self.AUTHORING_KEY = authoring_key_luis
        self.list_entities = list_entities
        self.list_intents = list_intents

        self.app_created = False
        self.app_published = False

        self.client = LUISAuthoringClient(self.AUTHORING_ENDPOINT, CognitiveServicesCredentials(self.AUTHORING_KEY))

        # information
        self.app_id = None
        self.app_version = None

        self.app_locale = None
        self.app_desc = None
        self.app_name = None
        
        self.endpoint=None
        self.publish_version = None

        self.RUNTIME_ENDPOINT = runtime_endpoint_luis
        self.RUNTIME_KEY = runtime_key_luis

        if self.RUNTIME_ENDPOINT and self.RUNTIME_KEY:
            self.client_runtimme = LUISRuntimeClient(self.RUNTIME_ENDPOINT, CognitiveServicesCredentials(self.RUNTIME_KEY))
        else:
            self.client_runtimme = None

    def create_app(self, name, description, version, local = "en-us",printing=False):
        '''
        '''
        self.app_id = self.client.apps.add(dict(name=name,
                                                initial_version_id=version,
                                                description=description,
                                                culture=local))
                                                        
        self.app_version = version
        self.app_locale = local
        self.app_desc = description
        self.app_name = name

        if printing:
            print("Création de l\'application LUIS: {}\nAvec l'ID: {}".format(self.app_name, self.app_id))

    def get_app(self,app_id):
        '''
        '''
        information = self.client.apps.get(app_id)

        self.app_created = True
        if information.endpoints:
            self.endpoint=information.endpoints["PRODUCTION"]["endpointUrl"]
            self.endpoint = self.endpoint +"?subscription-key=" + self.AUTHORING_KEY + "&q="
            self.app_published = True
        self.app_id = app_id
        self.app_version = information.active_version
        self.app_locale = information.culture
        self.app_desc = information.description
        self.app_name = information.name
    
    def _add_entities(self,printing=False):
        if self.app_created:
            for entity in self.list_entities:
                id_entity = self.client.model.add_entity(self.app_id, self.app_version, name=entity)
                if printing:
                    print("L\'entité {}  à était ajouté avec l\'ID : {} .".format(entity,id_entity))
        else:
            raise Exception("L\'application LUIS n'a pas était créé/récupérée, veuillez créer/récupérer l\'application avant toutes manipulation")

    def _add_intents(self,printing=False):
        if self.app_created:
            for entity in self.list_intents:
                id_entity = self.client.model.add_intent(self.app_id, self.app_version, name=entity)
                if printing:
                    print("L\'intents {}  à était ajouté avec l\'ID : {} .".format(entity,id_entity))
        else:
            raise Exception("L\'application LUIS n'a pas était créé/récupérée, veuillez créer/récupérer l\'application avant toutes manipulation")

    def _add_train_data(self,train_data):
        if self.app_created:
        
            if len(train_data) > 100 :
                for i in range(0,len(train_data),100):
                    j = (i+100)
                    if j > len(train_data):
                        j = len(train_data)
                    self.client.examples.batch(self.app_id,self.app_version,train_data[i:j])
            else:
                self.client.examples.add(self.app_id,self.app_version,train_data)
        else:
            raise Exception("L\'application LUIS n'a pas était créé/récupérée, veuillez créer/récupérer l\'application avant toutes manipulation")

    def train(self,train_data=None):
        '''
        '''
        if self.app_created:
            if train_data:
                self._add_train_data(train_data)
            self.client.train.train_version(self.app_id, self.app_version)
            waiting = True
            while waiting:
                info = self.client.train.get_status(self.app_id, self.app_version)

                # get_status returns a list of training statuses, one for each model. Loop through them and make sure all are done.
                waiting = any(map(lambda x: 'Queued' == x.details.status or 'InProgress' == x.details.status, info))
                if waiting:
                    print ("Waiting 10 seconds for training to complete...")
                    time.sleep(10)
                else: 
                    print ("trained")
                    waiting = False
            self.app_trained = True
        else:
            raise Exception("L\'application LUIS n'a pas était créé/récupérée, veuillez créer/récupérer l\'application avant toutes manipulation")
    
    def publish(self,is_staging=False,is_public = True,print_final_endpoint=False):
        '''
        '''
        self.client.apps.update_settings(self.app_id, is_public=is_public)

        responseEndpointInfo = self.client.apps.publish(self.app_id, self.app_version, is_staging=is_staging)
        self.endpoint = responseEndpointInfo.endpoint_url +"?subscription-key=" + self.AUTHORING_KEY + "&q="
        if print_final_endpoint:
            print(self.endpoint)
        return self.endpoint

    def evaluate(self,test_data):
        ''' Permet d'évaluer le modèle LUIS après entrainement et déploiement avec un jeu de données au format suivant:
        [{
            'text':'book a trip...',
            'intent_name': 'BookFlight',
            'entity_labels':[{
                'entity_name':'dst_city',
                'start_char_index':27
                'end_char_index':35
            },{
                'entity_name': 'or_city',
                'start_char_index': 41,
                'end_char_index': 48
            }]
        },
        ...
        ,{
            ...
        }]
        Parameters:
            test_data (list -> dict) : jeu de données de test au format ci-dessus

        Returns: 
            all_score (list -> float): correspond aux scores de l'accuracy du modèle pour chaque text
            mean_score (float) : correspond au score moyen obtenu

        '''
        # Calcul avec le predict si on peut
        if self.app_created and self.app_published:
            all_score = []
            for data in test_data:
                y_pred = self.predict(data["text"])
                y_true = self._format_y_true(data)
                score = self._calcul_score_accuracy(y_pred,y_true)
                all_score.append(score)
            mean_score = sum(all_score) / len(all_score)
            return all_score, mean_score
        else:
            raise Exception("L\'applicaiton n\'est pas disponnible, vérifier ça création ou sont déploiement.")

    def _format_y_true(self,y_true_data):
        y_true = {}
        text = y_true_data["text"]
        for entities in y_true_data["entity_labels"]:
            y_true[entities["entity_name"]] = text[entities["start_char_index"]:entities["end_char_index"]]
        
        return y_true

    def _calcul_score_accuracy(self,y_pred,y_true):
        score = 0
        for k,v in y_true.items():
            if k in y_pred:
                score += self._evaluate_value(v,y_pred[k])
            else:
                score += 0
        # accuracy
        accuracy_score = 1/len(y_true.keys()) * score
        return accuracy_score

    def _evaluate_value(self,data_true,data_pred):
        # Peu être améliorer en utilisant par exemple la méthode de levenshtein 
        # ou une autre méthode de simmilitude
        if data_true == data_pred:
            return 1
        elif data_true in data_pred:
            return 0.5
        else:
            return 0                    
        
    def predict(self,query,get_intent = False, timeout_seconde = 10):
        '''
        '''
        if self.client_runtimme:
            # On fait avec le client runtime SDK
            response = self.clientRuntime.prediction.get_slot_prediction(app_id=self.app_id,
                                                                        slot_name="production",
                                                                        prediction_request=query)
            y_pred = response.prediction.entities
            y_pred = {k:v[0] for k,v in y_pred.items()}
            if get_intent:
                intent = response.prediction.intents.keys()
                return y_pred, intent
            else:
                return y_pred
            
        else:
            response = None
            start = time.time()
            duration = 0
            # On boucle tant qu'on a pas une response mais un time out si pas de réponse valide
            while response == None and duration <= timeout_seconde:
                time.sleep(0.5)
                response = requests.get(self.endpoint + query)
                duration = time.time() - start
            response = response.json()
            y_pred = {}
            if "entities" in response:
                for entity in response["entities"]:
                    data = entity
                    key = data["type"]
                    value = data["entity"]
                    y_pred[key] = value
                    
                if get_intent:
                    intent = response["topScoringIntent"]["intent"]
                    return y_pred, intent
                else:
                    return y_pred
            # Sinon on appel le endpoint direct

