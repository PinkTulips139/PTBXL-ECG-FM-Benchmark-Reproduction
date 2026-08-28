import sys
from pathlib import Path
sys.path.append(str(Path().resolve() / "code"))

import numpy as np
import pandas as pd
from prettytable import PrettyTable

from clinical_ts.utils.bootstrap_utils import empirical_bootstrap
from clinical_ts.utils.eval_utils_cafa import multiclass_roc_curve
from clinical_ts.utils.eval_utils_regression import regression_metrics

import warnings
warnings.filterwarnings('ignore')


BASE_DIR = Path("") # CHANGE YOUR BASE_DIR

EVAL_MODE = "finetuning_linear" # CHANGE EVAL_MODE (finetuning_linear, frozen, linear, finetuning_nonlinear)
DATASET = "mimic"
MODELS = [
    "ecgfounder",
    "cpc"
]

def get_macro_auroc(targs, preds, classes):
    _, _, res = multiclass_roc_curve(targs, preds, classes=classes)
    return res["macro"]

def get_mae(targs, preds, metrics=["mae"], target_names=None):
    res = regression_metrics(targs, preds, metrics=metrics, target_names=target_names)
    return res["mae"]

output_dict = {DATASET: {}}

for k in output_dict.keys():
    for model in MODELS:
        file_path_dir = Path(BASE_DIR/ EVAL_MODE / f"{k}" / f"{model}" / "agg")
        npz_files = list(file_path_dir.glob("*.npz"))

        if not npz_files:
            raise FileNotFoundError(f"No .npz files found in {file_path_dir}")        

        content = dict(np.load(npz_files[0]))
        output_dict[k][model] = content


def compare_models_per_dataset_classification(y_true, model_preds_dict, classes=None, n_iterations=1000):
    auroc_score_dict = {
        k: get_macro_auroc(targs=y_true, preds=v, classes=classes) for k,v in model_preds_dict.items()
    }

    sorted_models = sorted(model_preds_dict.keys(), key=lambda x: auroc_score_dict[x], reverse=True)
    
    def find_equivalence_group(models_to_test, reference_model):
        equivalent_models = [reference_model]
        
        for model in models_to_test:
            if model == reference_model:
                continue
                
            _, score_low, score_high, _ = empirical_bootstrap(
                input_tuple=(y_true, model_preds_dict[reference_model]),
                score_fn=get_macro_auroc,
                input_tuple2=(y_true, model_preds_dict[model]),
                n_iterations=n_iterations,
                score_fn_kwargs={"classes": classes}
            )
            
            if score_low <= 0 <= score_high:
                equivalent_models.append(model)
        
        return equivalent_models
    
    ranks = {}
    remaining_models = sorted_models.copy()
    current_rank = 1
    
    while remaining_models:
        reference_model = remaining_models[0]        
        equivalent_models = find_equivalence_group(remaining_models, reference_model)
        
        for model in equivalent_models:
            ranks[model] = current_rank
            remaining_models.remove(model)
        
        current_rank += len(equivalent_models)
    
    best_model = sorted_models[0]
    model_status = {}
    for model in model_preds_dict.keys():
        score = auroc_score_dict[model]
        if model == best_model:
            style = "bold_underline"
        elif ranks[model] == ranks[best_model]:
            style = "bold"
        else:
            style = "plain"
        model_status[model] = [score, style, ranks[model]]
    
    return model_status

def compare_models_per_dataset_regression(y_true, model_preds_dict, classes=None, n_iterations=1000):
    mae_score_dict = {
        k: get_mae(targs=y_true, preds=v, metrics=["mae"]) for k,v in model_preds_dict.items()
    }

    sorted_models = sorted(model_preds_dict.keys(), key=lambda x: mae_score_dict[x])
    
    def find_equivalence_group(models_to_test, reference_model):
        equivalent_models = [reference_model]
        
        for model in models_to_test:
            if model == reference_model:
                continue
                
            _, score_low, score_high, _ = empirical_bootstrap(
                input_tuple=(y_true, model_preds_dict[model]),
                score_fn=get_mae,
                input_tuple2=(y_true, model_preds_dict[reference_model]),
                n_iterations=n_iterations,
                score_fn_kwargs={"metrics": ["mae"]}
            )
            
            if score_low <= 0 <= score_high:
                equivalent_models.append(model)
        
        return equivalent_models
    
    ranks = {}
    remaining_models = sorted_models.copy()
    current_rank = 1
    
    while remaining_models:
        reference_model = remaining_models[0]        
        equivalent_models = find_equivalence_group(remaining_models, reference_model)
        
        for model in equivalent_models:
            ranks[model] = current_rank
            remaining_models.remove(model)
        
        current_rank += len(equivalent_models)
    
    best_model = sorted_models[0]
    model_status = {}
    for model in model_preds_dict.keys():
        score = mae_score_dict[model]
        if model == best_model:
            style = "bold_underline"
        elif ranks[model] == ranks[best_model]:
            style = "bold"
        else:
            style = "plain"
        model_status[model] = [score, style, ranks[model]]
    
    return model_status

table_content = {}
first_model = list(output_dict[DATASET].keys())[0]

lbl_itos = output_dict[DATASET][first_model]["lbl_itos"]

cardiac_strings = ['I10','I25','I251','I2510','I48','I50','I489','I4891','I509','I12',
                    'I129','I503','I502','I95','I21','I252','I214','I27','I47','I5033',
                    'I42','I5023','I5032','I35','I34','I120','I73','I5022','I959','I44',
                    'I13','I4892','I278','I472','I739','I2789','I480','I11','I958','I70',
                    'I110','I130','I97','I82','I69','I20','I428','I359','I348','I9581',
                    'I702','I63','I978','I272','I45','I258','I08','I9789','I71','I504',
                    'I951','I87','I49','I26','I471','I269','I2511','I31','I699','I5021',
                    'I46','I24','I65','I200','I2699','I67','I447','I248','I652','I51',
                    'I259','I85','I469','I824','I872','I07','I340','I851','I350','I634',
                    'I5043','I255','I080','I442','I2582','I8510','I6999','I209','I714','I6529',
                    'I2581','I5031','I693','I078','I33','I330','I482','I61','I458','I451',
                    'I4510','I4581','I826','I211','I2720','I74','I6340','I77','I132','I429',
                    'I319','I490','I21A','I4901','I21A1','I441','I5030','I210','I2119','I2109',
                    'I678','I7020','I9589','I635','I7026','I518','I72','I6935','I5020','I619',
                    'I6350','I314','I80','I16','I081','I5042','I712','I952','I313','I6995',
                    'I440','I481','I808','I81','I672','I8261','I824Y','I7025']

noncardiac_strings = ['E78','E785','Z79','E11','E87','N17','Z87','N18','K21','K219',
            'Z878','Z8789','N179','Y92','Z790','E119','F32','F329','Z86','Z95',
            'Z7901','R07','Z85','Z867','E03','G47','J44','D64','J96','E039',
            'F41','Z794','N39','D649','F419','N390','R00','Y83','F172','F17',
            'E66','Z68','J449','N189','G473','Z66','Z98','G4733','E872','A41',
            'E871','D69','D62','J18','J45','E780','J189','E86','J459','Z798',
            'Z951','F10','R079','Y922','Y84','Y9223','E875','E669','N40','D63',
            'R001','Z8671','Z986','Z9861','F1720','R65','B96','G89','K59','R652',
            'K590','Z7982','Z91','M10','D696','J969','Z8673','M109','A419','R078',
            'E112','E116','M54','G93','N186','N400','J9690','R0789','N183','D72',
            'Z99','E83','Z7902','K5900','B95','G892','J960','D68','G8929','D50',
            'K76','D728','R10','R19','M81','J98','N170','M810','R6521','T82',
            'R09','Y848','Z78','E870','Z781','R33','E876','R11','E860','G92',
            'E114','Y929','R090','R0902','D7282','R197','Y920','G40','R6520','J69',
            'J690','F102','J4590','M79','R57','Z96','Z858','D631','Z90','M19',
            'R55','J4599','Z854','F05','J9601','R06','Z683','F1721','Y921','M199',
            'Z966','M1990','Z992','E1122','D509','E1165','Z955','E1140','F101','R13',
            'R131','G934','J91','Y838','R50','R74','K92','G470','R79','G4700',
            'K31','R339','L03','E13','Y9219','Z911','Z950','J95','E861','B37',
            'E88','L97','K56','Z8582','T81','L89','H40','Z23','F1010','Z9665',
            'E134','E1342','E113','J981','F039','F03','J958','G409','E46','E660',
            'Z684','E6601','J918','G4090','Z8546','K318','R791','Z51','F0390','H409',
            'R740','Y832','A04','Z918','R000','V43','F31','K74','Z9181','A047',
            'J441','K57','E10','R18','E1131','R41','B962','C78','R570','Z850',
            'Z82','R1310','K70','M25','K746','W18','C79','Z682','D638','R42',
            'R112','J15','E833','E8339','Z824','L031','B19','R188','Z92','E43',
            'Z958','L891','N99','Z8249','Z988','F11','K22','L8915','E877','R51',
            'M255','G43','F43','M549','Z515','D61','R53','R45','F319','N998',
            'M48','B18','B192','T45','D618','Z9581','K703','R78','E835','K573',
            'Y9200','G9340','R47','D689','R060','K766','B956','N184','K29','R29',
            'D6181','B1920','Y831','V17','R31','K72','R788','D695','Z795','D6959',
            'R7881','Z00','Z006','Z7952','V10','M545','K567','R101','M480','V103',
            'K7469','E873','Z9119','R91','Z89','B952','G439','G4390','J9819','G25',
            'T86','J9585','K80','V173','M06','Z922','N9982','Z9221','C34','J81',
            'E888','B968','T828','B182','D70','V70','V707','S06','R40','Z855',
            'E55','E559','R509','M069','E7800','K83','L0312','R298','F1020','N401',
            'E1129','V15','Y9209','R508','F02','F028','F1023','R63','V42','V46',
            'L975','R110','K86','F431','A415','R56','E1169','J90','T829','R569',
            'V153','X58','K65','E8889','F14','R94','M62','R109','T814','K3184',
            'K44','D684','E834','M47','B9689','R73','K7030','V436','V66','V667',
            'M796','Z874','Z8744','K5730','Y830','K85','M628','K921','K922','S22',
            'H54','K449','G81','M797','Z8503','B378','R538','V4364','R04','Z861',
            'D47','R458','F0280','R068','R4585','Z6841','T80','S72','F112','B9620',
            'K63','Z94','G936','M94','C795','M86','E115','R60','J84','R418',
            'R05','R002','R1013','G819','B9561','B961','E106','K91','V462','N13',
            'K64','R5081','R5383','C77','G62','T50','R32','K729','C92','F19',
            'E8779','K859','G9341','R26','B9629','C787','K55','E22','Z853','K52',
            'R62','R4182','E874','N08','G60','Z998','Z9981','D500','W184','W1849',
            'Z9889','R911','E222','Z904','N28','G30','R103','Y840','F34','J43',
            'M478','R0602','M7960','R338','H91','L27','F341','Z860','W183','E27',
            'V44','R634','R627','T861','D709','G309','R0689','E1151','Z8601','J439',
            'F141','Z45','R943','G258','Z9049','G609','J962','T451','H53','M35',
            'R470','Z9884','V433','Z851','E04','Z8511','L9750','Z450','C780','G2581',
            'T40','G20','R4701','M17','K5909','Z7989','M949','H919','A410','K768',
            'R20','J9811','E53','E1139','F1410','F1021','F1120','E8351','J9600','R2981',
            'V85','K75','R401','R730','H35','Z894','M4781','S01','R319','E538',
            'K58','Z681','W19','F12','F20','K3189','T802','K918','E104','R9431',
            'J984','E8770','Z72','M2551','K7689','J811','Z16','L40','T38','E880',
            'T8021','K762','R64','K20','B965','Z9114','Z80','G629','Z21','E89',
            'E1065','H9190','K66','R609','F06','M798','E8809','K227','D53','T83',
            'K2270','Z8551','Y928','T42','Z93','E8352','Z907','R471','D539','Z9664',
            'F199','R21','W1830','C7800','L974','T8612','K589','N25','Q21','Z871',
            'T17','F068','T88','T455','M4800','A4151','Z952','Y9289','D648','J810',
            'E890','S224','H353','K62','M84','K566','V45','R578','Z720','Y846',
            'M6282','T85','K50','E8342','Z8552','B3783','C91','E274','M51','Q211',
            'M12','K299','D630','R0600','K25','F4310','S065','K830','C90','C7952',
            'E102','V16','R040','C793','G31','B9562','B20','T36','C900','C7931',
            'R451','F111','K831','G893','T43','J152','M129','R531','K861','E21',
            'E44','M353','R34','J848','F90','K720','J069','J06','R918','Z8674',
            'J8489','N258','F4312','E05','R310','M4806','H3530','L271','J94','J980',
            'K7290','R269','J1521','K7200','F909','F1110','C61','E1121','E103','R748',
            'T827','C85','T380','Z6842','V422','K9189','T4551','L98','K529','N133',
            'K648','E1164','D473','Z8711','M542','J9691','M32','M179','A4101','T46',
            'L0311','K2990','Z895','J159','E1040','R82','R2989','Z8951','S32','T835',
            'K26','T8351','N1330','J9809','E1142','H548','K12','R7309','Z8942','R410',
            'A08','F25','S42','E2740','E16','Z76','S066','Z905','C9000','S82',
            'C22','S02','A40','Z9071','J9602','G4730','H26','J9581','N182','Z768',
            'Z7682','N2581','F01','F015','Z908','Z948','E440','N20','R579','C349',
            'T813','C25','R209','K7031','V60','E8349','T84','D46','J948','N31',
            'Z857','R1312','R1030','G318','K802','Y836','C858','F209','E041','H269',
            'Z923','K701','R798','K8020','K51','A418','D469','V420','C798','F1022',
            'F259','L9740','K123','E869','K43','R7989','R59','F432','T888','C3490',
            'D686','K920','K767','G91','Z8619','D86','B370','F60','R25','T811',
            'Z6843','V600','G935','K209','R68','C786','G931','Z4501','D89','C925',
            'K7291','Z901','K509','B957','J910','L033','M321','E162','K660','C911',
            'J9621','N319','D472','F39','C341','F33','T8286','N32','G891','R1011',
            'K5090','D75','Z59','V454','C7989','D721','T8285','Z9089','K7460','N289',
            'C7951','M7989','J47','M2556','H81','S721','F0150','B964','Z7984','D65',
            'T8289','C83','Z8614','R402','J38','Z590','D7281','N200','G82','K550',
            'M2555','F129','C9110','E213','K81','V64','N185','J80','Z8585','Y924',
            'R111','K651','B97','K635','M85','B00','Z940','K5660','V850','W01',
            'T402','Z993','Q23','C8589','T818','M858','Z4502','F410']


clinical_det = ['deterioration_severe_hypoxemia', 'deterioration_ecmo',
       'deterioration_vasopressors', 'deterioration_inotropes',
       'deterioration_mechanical_ventilation',
       'deterioration_cardiac_arrest']

icu = ['deterioration_icu_24h','deterioration_icu_stay']

mortality = ['deterioration_mortality_1d','deterioration_mortality_7d',
             'deterioration_mortality_28d','deterioration_mortality_90d',
             'deterioration_mortality_180d',
             'deterioration_mortality_365d',
             'deterioration_mortality_stay']
sex = ['sex']

age = ['age']

biometrics = ['Height (Inches)','Weight (Lbs)','BMI (kg/m2)']

ecg_features = ['RR','QRS','QT','QTc','P_wave_axis','QRS_axis','T_wave_axis']
    
lab_values = ['PT', 'Albumin', 'Anion Gap', 'Bicarbonate', 
              'Bilirubin, Total','Calcium, Total', 'Creatinine', 
              'Ferritin', 'Urea Nitrogen','Hematocrit', 
              'Hemoglobin', 'Lymphocytes', 'MCHC', 'RDW',
              'Red Blood Cells', 'RDW-SD', 'Creatine Kinase (CK)', 
              'NTproBNP']

vitals = ['dbp', 'heartrate', 'o2sat', 'resprate', 'sbp', 'temperature']

cardiac_indices = [i for i, label in enumerate(lbl_itos) if label in cardiac_strings]
noncardiac_indices = [i for i, label in enumerate(lbl_itos) if label in noncardiac_strings]
clinical_deterioration_indices = [i for i, label in enumerate(lbl_itos) if label in clinical_det]
mortality_indices = [i for i, label in enumerate(lbl_itos) if label in mortality]
icu_indices = [i for i, label in enumerate(lbl_itos) if label in icu]
sex_indices = [i for i, label in enumerate(lbl_itos) if label in sex]
age_indices = [i for i, label in enumerate(lbl_itos) if label in age]
biometrics_indices = [i for i, label in enumerate(lbl_itos) if label in biometrics]
ecg_features_indices = [i for i, label in enumerate(lbl_itos) if label in ecg_features]
lab_values_indices = [i for i, label in enumerate(lbl_itos) if label in lab_values]
vitals_indices = [i for i, label in enumerate(lbl_itos) if label in vitals]


print(f"No. of cardiac outcomes target: {len(cardiac_indices)}")
print(f"No. of non-cardiac outcomes target: {len(noncardiac_indices)}")
print(f"No. of clinical deterioration target: {len(clinical_deterioration_indices)}")
print(f"No. of mortality target: {len(mortality_indices)}")
print(f"No. of icu target: {len(icu_indices)}")
print(f"No. of sex target: {len(sex_indices)}")
print(f"No. of age target: {len(age_indices)}")
print(f"No. of biometrics target: {len(biometrics_indices)}")
print(f"No. of ecg features target: {len(ecg_features_indices)}")
print(f"No. of lab values target: {len(lab_values_indices)}")
print(f"No. of vitals target: {len(vitals_indices)}")

groups_class = {
    "cardiac": cardiac_indices,
    "noncardiac": noncardiac_indices,
    "clinical_deterioration": clinical_deterioration_indices,
    "icu": icu_indices,
    "mortality": mortality_indices,
    "sex": sex_indices
}

groups_reg = {
    "age": age_indices,
    "biometrics": biometrics_indices,
    "ecg_features": ecg_features_indices,
    "lab_values": lab_values_indices,
    "vitals": vitals_indices
}

n_iterations=1000

y_true = output_dict[DATASET][first_model]["targs"]
print(f"y_true shape: {y_true.shape}")

for group_name, group_indices in groups_class.items():
    
    print(group_name)
    
    model_preds_dict = {k: v["preds"][:, group_indices] for k, v in output_dict[DATASET].items()}
    y_true_group = y_true[:,group_indices]
    
    table_content[DATASET] = compare_models_per_dataset_classification(
    y_true=y_true_group,
    model_preds_dict=model_preds_dict,
    n_iterations=n_iterations)
    
    
    style_map = {
    "bold_underline": "(BU)",
    "bold": "(B)",
    "plain": "(P)"
    }

    models = list(output_dict[DATASET].keys())

    table = PrettyTable()
    table.field_names = ["Model", f"{DATASET} ({EVAL_MODE})", "Rank"]

    for model in models:
        if model in table_content[DATASET]:
            score, style, rank = table_content[DATASET][model]
            formatted_score = f"{score:.3f}{style_map.get(style, '')}"
        else:
            formatted_score = "-"
            rank = "-"

        row = [model, formatted_score, rank]
        table.add_row(row)

    print(table)


for group_name, group_indices in groups_reg.items():
    
    print(group_name)
    model_preds_dict = {k: v["preds"][:, group_indices] for k, v in output_dict[DATASET].items()}
    y_true_group = y_true[:,group_indices]
    
    table_content[DATASET] = compare_models_per_dataset_regression(
    y_true=y_true_group,
    model_preds_dict=model_preds_dict,
    n_iterations=n_iterations)
    
    
    style_map = {
    "bold_underline": "(BU)",
    "bold": "(B)",
    "plain": "(P)"
    }

    models = list(output_dict[DATASET].keys())

    table = PrettyTable()
    table.field_names = ["Model", f"{DATASET} ({EVAL_MODE})", "Rank"]

    for model in models:
        if model in table_content[DATASET]:
            score, style, rank = table_content[DATASET][model]
            formatted_score = f"{score:.3f}{style_map.get(style, '')}"
        else:
            formatted_score = "-"
            rank = "-"

        row = [model, formatted_score, rank]
        table.add_row(row)

    print(table)

