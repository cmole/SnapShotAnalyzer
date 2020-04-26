import boto3

def getSessions():
    
    session = boto3.Session(profile_name='shotty')
    ec2 = session.resource('ec2')

    for i in ec2.instances.all():
        print(i)
    
    return ec2.instances.all()


if __name__ == '__main__':
    print("initializing")
    
