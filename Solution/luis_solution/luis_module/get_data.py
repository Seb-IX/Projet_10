import pandas as pd

class LuisData:
    def __init__(self,data_path : str):
        '''Cette classe permet la manipulation du jeu de données pour le contexte de la création d\'un chatbot implémentant l\'outil LUIS Azure 
        Parameters:
            data_path (str):

        Returns:
            None
        '''
        self.data_path = data_path

        self.turns_list_create = False
        self.data_transformed = False
        self.data_loaded = False

        self.df_data = None
        self.data_luis = None
        self.turns_list = None

    def load_data(self):
        '''Cette fonciton permet le chargement du fichier frame.json contenant les différentes conversations entre l\'utilisateur et l\'assistant
        
        Parameters: 
            None

        Returns:
            None
        '''
        self.df_data = pd.read_json(self.data_path)
        self.data_loaded = True
        satisfaction_df = pd.json_normalize(self.df_data["labels"])
        self.df_data["userSurveyRating"] = satisfaction_df["userSurveyRating"]
        self.df_data["wizardSurveyTaskSuccessful"] = satisfaction_df["wizardSurveyTaskSuccessful"]
        self.df_data.drop("labels",axis=1,inplace=True)
        # On récupére uniquement les dialogues
        turns_serie = self.df_data['turns']
        self.turns_list = turns_serie.to_list()
        self.turns_list_create = True

    def get_data(self):
        '''Getter du dataframe du jeu de données frame.json
        '''
        if not self.data_loaded:
            self.load_data()
        return self.df_data


    def get_turns(self):
        '''Getter des turns du jeu de données frame.json
        '''
        if not self.data_loaded:
            self.load_data()
        return self.turns_list

    def _format_data_luis(self,intent, text, labels):
        '''Cette fonction permet le formatage des dialogues au format de données LUIS
        
        Parameters:
            intent (str) : intention utilisateur, qui correspond au nommage LUIS pour l\'apprentissage, (définit le domaine d\'intention)
            text (str) : texte formulé par l\'utilisateur
            labels (list/tuple => tuple) : liste des labels récupérés du texte utilisateur avec la clé correspondante

        Returns:
            format_data (dict) : retourne un format de données utilisable par LUIS => 
            {
                \'texte\':\'le texte de l'utilisateur.\',
                \'intent_name\'=\'Exemple\',
                \'entity_labels\':[
                    {
                        \'entity_name':\'wordText\',
                        \'start_char_index\':3,
                        \'end_char_index\':8
                    }
                ]
            }
        '''
        text = text.lower()

        def entity_format(name, value):
            '''Cette fonction est une fonction interne pour formater les entity_label
            '''
            # on récupére la taille et le début de l'index de la value sur le text pour avoir le début et la fin de la value dans le texte
            value = value.lower()
            start = text.index(value)
            return dict(entity_name=name, start_char_index=start,
                        end_char_index=start + len(value))

        return dict(text=text, intent_name=intent,
                    entity_labels=[entity_format(n, v) for (n, v) in labels])

    def transform_data(self,reload=False):
        '''Cette fonction permet le formatage du jeu de données

        Parameters:
            reload (bool, optionnel) : Permet de forcer le rechargement des données
        Returns:
        
        '''
        if not self.turns_list_create:
            self.load_data()

        if not self.data_transformed or reload:
            final_data = []
            for conversation in self.turns_list:
                for message in conversation:
                    # On récupére uniquement les echanges du user
                    if message["author"] == "user":
                        text = message["text"]
                        acts = message["labels"]["acts"]
                        conversation_list = []
                        for act in acts:
                            if act["args"]:
                                for arg in act["args"]:
                                    if not arg["key"] == "ref":
                                        data = self._get_key_value(arg)
                                        if data:
                                            conversation_list.append(data)
                                    else:
                                        annotations_list = arg['val'][0]['annotations']
                                        if annotations_list:
                                            for annotation_value in annotations_list:
                                                data = self._get_key_value(annotation_value)
                                            if data:
                                                conversation_list.append(data)
                        if conversation_list:
                            final_data.append(self._format_data_luis("BookFlight", text, conversation_list))
            self.data_luis = final_data

        return self.data_luis

    def _get_key_value(self,arg):
        '''On recupère la clé et valeur de l\'argument fournit pour les clés suivantes : "dst_city","or_city","str_date","end_date","n_adult","n_children","budget","seat"

        Parameters :
            arg (tuple) : argument de l\'intention utilisateur au format tuple.
            
        Returns:
            key_value (tuple) : retourne la clé/valeur de l\'argument au format tuple si il correspond à la liste de clé.
            OR
            None : si la valeur n'est pas formatée correctement ou que la clé n\'est pas dans la liste citée précédemment
        '''
        list_key = ['dst_city','or_city','str_date','end_date','n_adult','n_children','budget','seat']
        if "key" in arg and "val" in arg:
            if arg["key"] in list_key and arg['val'] != "-1" and arg['val'] != None:
                return (arg["key"],arg["val"])
        return None

    
    def create_data_luis_from_other_file(self,data_path_txt):
        pass
