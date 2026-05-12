import json
import boto3

runtime = boto3.client('sagemaker-runtime')
ENDPOINT_NAME = 'power-plant-endpoint'

RENEWABLES = {'Solar', 'Wind', 'Hydro', 'Geothermal', 'Tidal', 'Biomass'}

IMPUTE_COMMISSION_YEAR = 1996.0
IMPUTE_OWNERSHIP = 'Private'
IMPUTE_REGION = 'Europe'

FUEL_TYPES  = ['Biomass','Coal','Gas','Geothermal','Hydro','Nuclear','Oil','Solar','Storage','Tidal','Waste','Wind']
OWNER_TYPES = ['Government','Independent Power Producer','Private','Public-Private Partnership','State-Owned Enterprise']
STATUS_TYPES = ['Decommissioned','Operating','Planned','Standby','Under Construction']
REGIONS = ['Africa','Central America','East Asia','Europe','Europe/Asia','Middle East','North America','Oceania','South America','South Asia','Southeast Asia']

def one_hot(value, categories):
    return [1.0 if value == c else 0.0 for c in categories]

def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    capacity_mw = float(body['capacity_mw'])
    primary_fuel = body['primary_fuel']
    commissioning_year = float(body.get('commissioning_year', IMPUTE_COMMISSION_YEAR))
    latitude = float(body['latitude'])
    longitude = float(body['longitude'])
    ownership_type = body.get('ownership_type', IMPUTE_OWNERSHIP)
    status = body.get('status', 'Operating')
    region = body.get('region', IMPUTE_REGION)
    
    plant_age = 2026 - commissioning_year
    is_renewable = 1.0 if primary_fuel in RENEWABLES else 0.0
    
    features = [capacity_mw, latitude, longitude, plant_age, is_renewable]
    features.extend(one_hot(primary_fuel, FUEL_TYPES))
    features.extend(one_hot(ownership_type, OWNER_TYPES))
    features.extend(one_hot(status, STATUS_TYPES))
    features.extend(one_hot(region, REGIONS))
    
    payload = ','.join(str(f) for f in features)
    
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType='text/csv',
        Body=payload
    )
    
    prediction = float(response['Body'].read().decode().strip())
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'predicted_generation_gwh': round(prediction, 2),
            'input_summary': {
                'capacity_mw': capacity_mw,
                'primary_fuel': primary_fuel,
                'plant_age': int(plant_age),
                'region': region
            }
        })
    }