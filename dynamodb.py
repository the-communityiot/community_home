# Add user details into loginauth table
def registeruser(email, username, password):
    try:
        import boto3
        from boto3.dynamodb.conditions import Key, Attr

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('loginauth')

        response = table.put_item(
            Item={
                'email': email,
                'username': username,
                'password': password
            }
        )
        return response
    except:
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

# Add license plate into licensedata table
def addlicenseplate(licensenumber):
    try:
        import boto3
        from boto3.dynamodb.conditions import Key, Attr

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('licensedata')

        response = table.put_item(
            Item={
                'licenseid': "licenseid_community",
                'license': licensenumber
            }
        )
        return response
    except:
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

# Delete license plate from licensedata table
def deletelicenseplate(licensenumber):
    try:
        import boto3
        from boto3.dynamodb.conditions import Key, Attr

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('licensedata')
        response = table.delete_item(
            Key={
                'licenseid': "licenseid_community",
                'license': licensenumber
            }
        )
        return response
    except:
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

# Delete user from loginauth table
def deleteuser(email):
    try:
        import boto3
        from boto3.dynamodb.conditions import Key, Attr
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('loginauth')
        response = table.delete_item(
            Key={
                'email': email
            }
        )
        return response
    except:
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

# Get login details from loginauth table (Email and password)
def getlogin(email, password):
    try:
        import boto3
        from boto3.dynamodb.conditions import Key, Attr

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('loginauth')

        response = table.query(
            KeyConditionExpression=Key('email').eq(email)
        )

        items = response['Items']
        email = items[0]['email']
        password = items[0]['password']
        return (password, email)
    except:
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

# Get login details from loginauth table (Email and username)
def get_data_from_dynamodb_users():
    try:
        import boto3
        from boto3.dynamodb.conditions import Key, Attr
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('loginauth')
        response = table.scan(AttributesToGet=['email', 'username'])
        items = response['Items']
        return items

    except:
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

# Get temperature data from temperaturedata table
def get_data_from_dynamodb_temperature():
    try:
        import boto3
        from boto3.dynamodb.conditions import Key, Attr

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('temperaturedata')
        startdate = '2021-02'
        response = table.query(
            KeyConditionExpression=Key('tempid').eq('tempid_community')
            & Key('datetimeid').begins_with(startdate),
            ScanIndexForward=False
        )
        items = response['Items']
        n = 10  # limit to last 10 items
        data = items[:n]
        data_reversed = data[::-1]
        return data_reversed
    except:
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

# Get temperature data from temperaturedata table
def get_data_from_dynamodb_temperatureone():
    try:
        import boto3
        from boto3.dynamodb.conditions import Key, Attr

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('temperaturedata')
        startdate = '2021-02'
        response = table.query(
            KeyConditionExpression=Key('tempid').eq('tempid_community')
            & Key('datetimeid').begins_with(startdate),
            ScanIndexForward=False
        )
        items = response['Items']
        n = 1  # limit to last 10 items
        data = items[:n]
        data_reversed = data[::-1]
        return data_reversed
    except:
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

# Get license data from licensedata table
def get_data_from_dynamodb_license():
    try:
        import boto3
        from boto3.dynamodb.conditions import Key, Attr
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('licensedata')
        response = table.query(
            KeyConditionExpression=Key('licenseid').eq('licenseid_community'),
            ScanIndexForward=False
        )
        items = response['Items']
        return items
    except:
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

# Get light data from lightdata table
def get_data_from_dynamodb_Light():
    try:
        import boto3
        from boto3.dynamodb.conditions import Key, Attr
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('lightdata')

        startdate = '2021-02'

        response = table.query(
            KeyConditionExpression=Key('lightid').eq('lightid_community')
            & Key('datetimeid').begins_with(startdate),
            ScanIndexForward=False
        )

        items = response['Items']

        n = 10
        data = items[:n]
        data_reversed = data[::-1]

        return data_reversed
    except:
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

# Get DayNight status from DayNightTable table
def get_data_light_night():
    try:
        import boto3
        from boto3.dynamodb.conditions import Key, Attr
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('DayNightTable')

        response = table.query(
            KeyConditionExpression=Key('DayNightID').eq('daynight_community')
        )

        items = response['Items']
        daynight = items[0]['mode']
        return(daynight)
    except:
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

if __name__ == "__main__":
    get_data_from_dynamodb()
