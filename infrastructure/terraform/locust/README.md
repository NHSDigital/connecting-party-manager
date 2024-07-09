# Basic load test setup

Due to time issues at the point of making this its currently quite a manual process to start this setup

## 1. Download the pem file

There is a locust-key.pem file stored in the MGMT secrets - download this to your machine as it will be used to SSH onto the EC2 instances later

## 2. Upload your locustfile.py

In the load_test folder at the top level there is a locustfile.py - make your adjustments and then upload it to the following s3 bucket:

- nhse-cpm--mgmt--locust-file

It will replace whatever is in there so make sure you check with the team before doing that

## 3. Start the Ec2 instances

Navigate to this folder and do the following

- Go to the SSO console and copy the MGMT key details (the section that gives you a bunch of export values)
- Paste that into your terminal window
- Run terraform plan - this should show 4 resources atm as the default number of workers is 3, if you want to change this number go to vars.tf and adjust the number
- Run terraform apply
- Make note of the master IP

## 4. Add your IP to the security group

There is a Security Group that sits in the MGMT infrastructure that you will need to add your IP address to so that you can SSH onto the boxes

To do this naviagate to security groups and locate the Locust group

Add a new ingress rule and set it to port 22 or SSH and then in the field with the magnifying glass there will be an option for "My IP" select that and save it

## 5. Start the master node

Now you will want to SSH onto the master node using the pem file you downloaded and the master IP - below is an example of how I did it, make sure your path is correct and the ip address matches the master node

`ssh -i path/to/locust-key.pem ubuntu@<MASTER_NODE_IP>`

Once you have gained access run the following command

`locust -f locustfile.py --master --host=<base url for endpoint> --apikey=<Apigee app API key for the host>`

An example for --host would be `https://internal-dev.api.service.nhs.uk/cpm-dev`

This should then tail the master log in your terminal, keep this one open

## 6. Start the worker nodes

Its the same process as step 5 except you need to go onto each worker node and start them with the following command

`locust -f locustfile.py --worker --host=<base url for endpoint> --apikey=<Apigee app API key for the host> --master-host=<IP of master node>`

Probably worth having a terminal open for each one - or you can run them --headless

## 7. Go to the dashboard and start your test

Once the master node is setup you will have access to the Locust dashboard - you can find it by going to your browser and entering

`<Master node ip>:8089`

This then lets you change any of the above variables and the number of users etc, then you can start the test and get the feedback
