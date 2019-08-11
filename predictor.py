import os
import numpy as np
import boto3
from file_manager import FileManager
from botocore.exceptions import ClientError
from fastai.vision import load_learner, open_image

class Predictor:

    def __init__(self, image, num_results=5):
        self.image = image
        self.num_results = num_results
        self.model_file = 'greenlight_model.pkl'
        self.s3_client = boto3.client(
            's3', 
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'), 
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name=os.getenv('AWS_REGION')
        )

    '''
    Gets x top predictions and confidence scores for image
    '''
    def get_top_predictions(self):
        
        # list of classes
        classes = ['buick_century', 'buick_enclave', 'buick_lacrosse', 'buick_lesabre', 'buick_lucerne', 'buick_parkavenue', 'buick_regal', 'buick_rendezvous', 'buick_verano', 'cadillac_cts', 'cadillac_escalade', 'cadillac_srx', 'cadillac_sts', 'chevrolet_avalanche', 'chevrolet_aveo', 'chevrolet_blazer', 'chevrolet_camaro', 'chevrolet_cavalier', 'chevrolet_cobalt', 'chevrolet_colorado', 'chevrolet_corvette', 'chevrolet_cruze', 'chevrolet_equinox', 'chevrolet_hhr', 'chevrolet_impala', 'chevrolet_malibu', 'chevrolet_montecarlo', 'chevrolet_s10', 'chevrolet_silverado', 'chevrolet_sonic', 'chevrolet_suburban', 'chevrolet_tahoe', 'chevrolet_trailblazer', 'chevrolet_traverse', 'chevrolet_uplander', 'chrysler_200', 'chrysler_300', 'chrysler_pacifica', 'chrysler_pt cruiser', 'chrysler_sebring', 'chrysler_town&country', 'dodge_avenger', 'dodge_caliber', 'dodge_challenger', 'dodge_charger', 'dodge_d250', 'dodge_dakota', 'dodge_dart', 'dodge_durango', 'dodge_grand caravan', 'dodge_journey', 'ford_bronco', 'ford_edge', 'ford_escape', 'ford_excursion', 'ford_expedition', 'ford_f150', 'ford_fiesta', 'ford_five hundred', 'ford_focus', 'ford_fusion', 'ford_mustang', 'ford_ranger', 'ford_taurus', 'ford_thunderbird', 'gmc_acadia', 'gmc_envoy', 'gmc_jimmy', 'gmc_sierra_2500', 'gmc_sierra_3500', 'gmc_yukon_1500', 'gmc_yukon_2500', 'honda_accord', 'honda_civic', 'honda_cr-v', 'honda_odyssey', 'honda_pilot', 'hyundai_elantra', 'hyundai_santafe', 'hyundai_sonata', 'jeep_compass', 'jeep_grand_cherokee', 'jeep_patriot', 'kia_soul', 'lincoln_mks', 'lincoln_mkx', 'lincoln_mkz', 'lincoln_navigator', 'lincoln_towncar', 'mercury_grandmarquis', 'mercury_mariner', 'mercury_mountaineer', 'mercury_sable', 'nissan_altima', 'nissan_frontier', 'nissan_maxima', 'nissan_murano', 'nissan_pathfinder', 'nissan_sentra', 'nissan_titan', 'pontiac_g6', 'pontiac_grandam', 'pontiac_grandprix', 'pontiac_montana', 'pontiac_torrent', 'pontiac_vibe', 'saturn_ion', 'saturn_outlook', 'saturn_vue', 'subaru_forester', 'subaru_outback', 'toyota_camry', 'toyota_corolla', 'toyota_highlander', 'toyota_prius', 'toyota_rav4', 'toyota_sienna', 'toyota_tacoma', 'toyota_tundra', 'volkswagen_jetta', 'volkswagen_passat']
        
        # generate predictions using model (learner)
        learner = self.get_learner()
        img = open_image(self.image)
        prediction = learner.predict(img)
        
        # create dictionary with all prediction scores
        prediction_probabilities = {
            'index': [],
            'class': [],
            'score': []
        }

        for index in range(len(prediction[2])):
            prediction_probabilities['index'].append(index)
            prediction_probabilities['class'].append(classes[index])
            prediction_probabilities['score'].append(float(prediction[2][index]))

        # get top scores and classes
        top_x_idx = np.argsort(prediction_probabilities['score'])[-self.num_results:]    
        top_x = {}
        for i in top_x_idx:
            top_x[classes[i]] = prediction_probabilities['score'][i]
        
        return top_x

    def get_learner(self):        
        return load_learner('uploads', self.model_file)