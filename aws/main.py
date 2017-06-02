
from scenarios import Scenarios
from aws import AWSModel

def main():
    s = Scenarios()
    print s.aws_scenario_1()
    # s.aws_scenario_2(5)
    # awsm = AWSModel()
    # print (awsm.ec2instances())

if __name__ == "__main__":
    main()
