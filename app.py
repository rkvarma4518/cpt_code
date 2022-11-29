from flask import Flask,request
import sqlite3
from flask_restful import Api, Resource, reqparse
from fuzzywuzzy import fuzz
import pandas as pd

app = Flask(__name__)
app.secret_key = 'shri'
api = Api(app) ## make api using flask_restful


class Code(Resource):
    def get(self, des):
        item = Code.find_by_desription([des])
        if item:
            return item
        return {"message":"given named Porcedure dosen't match any procedure!"}, 400

    @classmethod
    def find_by_desription(cls, pre_procedure):
        #CPT code Data from database
        connection = sqlite3.connect('updated_cpt_data.db')
        cursor = connection.cursor()
        query = 'select * from cpt_code'
        cursor.execute(query)
        result = cursor.fetchall()
        cpt_data = pd.DataFrame(result, columns=['code','procedure'])     #to DataFrame
        connection.commit()
        connection.close()

        #list for temp storage
        ratio_list = []
        proc_list = []
        db_proc_list = []
        code_list = []
        for proc in pre_procedure:
            try:
                temp_ratio_list = []
                temp_proc_list = []
                temp_db_proc_list = []
                temp_code_list = []
                for i in range(len(cpt_data['procedure'])):
                    db_proc = str(cpt_data['procedure'][i])
                    l = set(db_proc.split())
                    l2 = set(proc.split())
                    common = l.intersection(l2)
                    if len(common) > 0:
                        cptcode = cpt_data['code'][i]
                        ratio = fuzz.ratio(proc, db_proc)
                        if ratio > 74:
                            temp_ratio_list.append(ratio)
                            temp_proc_list.append(proc)
                            temp_db_proc_list.append(db_proc)
                            temp_code_list.append(cptcode)
                    
                if len(temp_ratio_list) >0:
                    max_ratio = max(temp_ratio_list)
                    ratio_ind = temp_ratio_list.index(max_ratio)
                    procedure = temp_proc_list[ratio_ind]
                    db_procedure = temp_db_proc_list[ratio_ind]
                    code = temp_code_list[ratio_ind]
                    ratio_list.append(max_ratio)
                    proc_list.append(procedure)
                    db_proc_list.append(db_procedure)
                    code_list.append(code)
                else:
                    pass
            except Exception as e:
                print(e)
            
        result = {
            'code': code_list,
            'procedure': proc_list,
            'db_procedure': db_proc_list,
            'Score': ratio_list,
        }

        return result
 
## add endpoints
api.add_resource(Code, '/code/<string:des>') 

if __name__=='__main__':
    app.run()