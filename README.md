## SnapShotAnalyzer
Tool to manage EC2 snapshots and instances

## About

This is a demo project to manage EC2 instances & snapshots.  It uses the boto3 tool to connect to AWS

## Configuring
shotty uses the configuration file created by the AWS cli e.g.

`aws configure -- profile shotty`

## Running
This requires PipEnv to execute

`pinenv install`
`pipenv run python shotty/shotty.py <command> <subcommand> <--project=PROJECT>`

*command* instances, volumes, snapshots
*subcommand* depeds on command
*project is optional