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
def cli():
    """shotty manages snapshots"""
    pass

@cli.group('instances')
def instances():
    """Commands for Instances"""
    pass

@instances.command('list')
@click.option('--project', default=None,
    help='Only instances for project (tag Project:<name>)')
def list_sessions(project):
    "List EC2 Instances"
    
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
    return


@instances.command('stop')
@click.option('--project', default=None,
    help='Only instances for project (tag Project:<name>)')
def stop_sessions(project):
    "Stop EC2 Instances"

    instances = getInstances(project)
    for i in instances:
        i.stop()
    return

@instances.command('start')
@click.option('--project', default=None,
    help='Only instances for project (tag Project:<name>)')
def start_sessions(project):
    "Start EC2 Instances"

    instances = getInstances(project)
    for i in instances:
        i.start()
    return


@cli.group('volumes')
def volumes():
    """Commands for volumes"""
    pass


@volumes.command('list')
@click.option('--project', default=None,
    help='Only instances for project (tag Project:<name>)')
def list_volumes(project):
    "List EC2 Volumes"
    
    instances = getInstances(project)
    for i in instances:
        for v in i.volumes.all():
            print(', '.join((
                i.id,
                v.id,
                v.state,
                str(v.size) + 'GiB',
                v.encrypted and "Encrypted" or "Not Encrypted"
                )))
    return


@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""
    pass

@snapshots.command('list')
@click.option('--project', default=None,
    help='Only instances for project (tag Project:<name>)')
def list_snapshots(project):
    "List EC2 snapshots"
    
    instances = getInstances(project)
    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():            
                print(', '.join((
                    i.id,
                    v.id,
                    s.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))
    return

if __name__ == '__main__':
    cli()