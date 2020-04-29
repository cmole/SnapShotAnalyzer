import boto3
import botocore
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

def has_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'


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
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(" Could not stop {0}.".format(i.id) + str(e))
            continue
    return

@instances.command('start')
@click.option('--project', default=None,
    help='Only instances for project (tag Project:<name>)')
def start_sessions(project):
    "Start EC2 Instances"

    instances = getInstances(project)
    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(" Could not stop {0}.".format(i.id) + str(e))
            continue
    return

@instances.command('snapshot')
@click.option('--project', default=None,
    help='Only instances for project (tag Project:<name>)')
def create_snapshot(project):
    "Create snapshots for EC2 instances"

    instances = getInstances(project)
    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
            i.wait_until_stopped()
            for v in i.volumes.all():
                if has_pending_snapshot(v):
                    print("  Existing snapshot in progress.  Skipping {0} snapshot.".format(v.id))
                    continue
                print("  Creating snapshot of {0}".format(v.id))
                v.create_snapshot(Description="Created by snappy")
            
            print("Starting {0}...".format(i.id))
            i.start()
        except botocore.exceptions.ClientError as e:
            print(" Error processing {0}.".format(i.id) + str(e))
            continue
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
@click.option('--all', 'list_all', default=False, is_flag=True,
    help='List all snapshots for each volume, not just the most recent)')
def list_snapshots(project, list_all):
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
                if s.state == 'completed' and not list_all: break
    return


@snapshots.command('delete')
@click.option('--project', default=None,
    help='Only instances for project (tag Project:<name>)')
def delete_snapshots(project):
    "Delete EC2 snapshots"
    
    instances = getInstances(project)
    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():            
                if s.state == 'pending':
                    print("Skipping pending snapshot {0}".format(v.id))
                    continue
                
                print("Deleting snapshot: " + ', '.join((
                    i.id,
                    v.id,
                    s.id)))
                s.delete()
    return


if __name__ == '__main__':
    cli()