import boto3
import uuid
import os
import json

def lambda_handler(event, context):
    # Entrada (json)
    print(event)
    tenant_id = event['body']['tenant_id']
    texto = event['body']['texto']
    
    # Variables de entorno por stage
    nombre_tabla = os.environ["TABLE_NAME"]
    nombre_bucket = os.environ["BUCKET_NAME"]
    
    # Proceso
    uuidv1 = str(uuid.uuid1())
    comentario = {
        'tenant_id': tenant_id,
        'uuid': uuidv1,
        'detalle': {
          'texto': texto
        }
    }
    
    # 1. Grabar en DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(nombre_tabla)
    response_db = table.put_item(Item=comentario)
    
    # 2. Ingesta Push: Grabar archivo JSON en el bucket S3 correspondiente
    s3 = boto3.client('s3')
    # Guardamos el archivo organizándolo por tenant_id
    nombre_archivo = f"{tenant_id}/{uuidv1}.json"
    
    response_s3 = s3.put_object(
        Bucket=nombre_bucket,
        Key=nombre_archivo,
        Body=json.dumps(comentario, ensure_ascii=False),
        ContentType='application/json'
    )
    
    # Salida (json)
    print(comentario)
    return {
        'statusCode': 200,
        'comentario': comentario,
        'response_db': response_db,
        'archivo_s3': nombre_archivo,
        'bucket_destino': nombre_bucket
    }
