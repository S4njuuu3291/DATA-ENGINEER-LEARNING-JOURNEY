def lambda_handler(event, context):
    # Hello world dalam berbagai bahasa
    print("Hello, Dunia!")
    print("Hello, World!")
    print("Hola, Mundo!")
    print("Bonjour, le Monde!")
    print("Hallo, Welt!")
    print("Ciao, Mondo!")

    return {
        'statusCode': 200,
        'body': 'Hello, Dunia! from AWS Lambda'
    }
    