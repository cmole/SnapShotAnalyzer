import boto3
import click


session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def getInstances(project):
    instances = []
    
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

@click.group()
def instances():
    """Commands for instances"""

@instances.command('list')
@click.option('--project', default=None,
    help='Only instances for project (tag Project:<name>)')
def list_sessions(project):
    "List EC2 Sessions"
    
    instances = getInstances(project)
    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            tags.get('Project', '<no project>'),
            i.public_dns_name))
        )
    
@instances.command('stop')
@click.option('--project', default=None,
    help='Only instances for project (tag Project:<name>)')
def stop_sessions(project):
    "Stop EC2 Sessions"

    instances = getInstances(project)
    for i in instances:
        i.stop()

@instances.command('start')
@click.option('--project', default=None,
    help='Only instances for project (tag Project:<name>)')
def start_sessions(project):
    "Start EC2 Sessions"

    instances = getInstances(project)
    for i in instances:
        i.start()

if __name__ == '__main__':
    instances()
    instances()
instances