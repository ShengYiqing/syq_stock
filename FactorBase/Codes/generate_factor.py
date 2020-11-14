import os
import sys
import datetime


def main(start_date, end_date):
    factor_list = os.listdir('../')
    for factor_name in factor_list:
        if (factor_name != '.ipynb_checkpoints') & (factor_name != 'Codes'):
            string1 = 'cd ../%s/Codes/'%factor_name
            string2 = 'python generate_factor.py %s %s'%(start_date, end_date)
            s = string1 + '\n' + string2
            with open('a.bat', 'w') as f:
                f.write(s)
            os.system('a.bat')
            #os.system('python ../%s/Codes/generate_factor.py %s %s'%(factor_name, start_date, end_date))

if __name__ == '__main__':
    if len(sys.argv) == 3:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
    elif len(sys.argv) == 2:
        start_date = sys.argv[1]
        end_date = sys.argv[1]
    elif len(sys.argv) == 1:
        start_date = datetime.datetime.today().strftime('%Y%m%d')
        end_date = datetime.datetime.today().strftime('%Y%m%d')
    else:
        print('date?')
        exit()
    print(os.listdir('../'))
    main(start_date, end_date)