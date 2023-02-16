# safe_evaluation

safe_evaluation - is an implementation of polish notation algorithm for mathematical and dataframe operations

# how to use

1. Installation
    ```
    pip install safe-evaluation
    ```
2. Tutorial 
   - import evaluation class
    ```
    from safe_evaluation import Evaluator
    ```
   - initialize evaluator
    ```
    evaluator = Evaluator()
    ```
   - send string that you want to evaluate
    ```
    result = evaluator.solve(command="2 + 2")
    ```
   - method will return result
    ```
    print(result)
    ```
3. Examples of usage
   -  ```
      evaluator.solve(command="2 + 2")  # 4
      ```
   -  ```
      evaluator.solve(command="lambda x: x * 2")  # lambda x: x * 2
      ```
   -  ```
      evaluator.solve(command="2 * x - y", local={"x": 2, "y": 3})  # 1
      ```

   -  ```
      import pandas as pd

      df = pd.DataFrame(data={'col1': [1, 2], 'col2': [3, 4]})
      evaluator.solve(command="${col1} + ${col2}", df=df)  # 0   4
                                                              1   6
                                                              dtype: int64
      ```
   -  ```
      evaluator.solve(command="list(map(lambda x, y: x * 2 + y, range(5), range(3, 8)))")  # [3,6,9,12,15]
      ```
   -  ```
      evaluator.solve(command="list(map(lambda x: x + y, [0,1,2,3,4]))", local={"y": 10})  # [10,11,12,13,14]
      ```
   -  ```
      import pandas as pd
     
      df = pd.DataFrame(data={'col1': [1, 2, 4, 7], 'col2': [3, 4, 8, 9]})
      evaluator.solve(command="np.mean(${col1}) + np.mean(${col2})", df=df)  # 9.5
      ```
   -  ```
      import pandas as pd
     
      df = pd.DataFrame(data={'col1': [1, 2, 4, 7], 'col2': [3, 4, 8, 9]})
      evaluator.solve(command="${col1}.apply(lambda v: v ** 2 > 0).all()", df=df)  # True
      ```
   -  ```
      import pandas as pd
     
      df = pd.DataFrame(data={'col1': [1, 2, 4, 7], 'col2': [3, 4, 8, 9]})
      evaluator.solve(command="${col1}.apply(lambda v: 1 if v < 3 else 2)", df=df)  # 0    1
                                                                                       1    1
                                                                                       2    2
                                                                                       3    2
                                                                                       Name: col1, dtype: int64
      ```
   -  ```
      from datetime import datetime

      import pandas as pd
      
      dates = [datetime(year=2022, month=11, day=11 + i) for i in range(7)]
      df = pd.DataFrame(data={'dates': dates})
      evaluator.solve(command="${dates}.dt.dayofweek", df=df)  # 0    4
                                                                  1    5
                                                                  2    6
                                                                  3    0
                                                                  4    1
                                                                  5    2
                                                                  6    3
                                                                  Name: dates, dtype: int64
      ```
   -  ```
      range = evaluator.solve(command="pd.date_range(start='2021-02-05', end='2021-03-05', freq='1D')"")
      len(range)  # 29
      ```
   
   -  ```
      df = pd.DataFrame(data={'col1': [1, 2], 'col2': [3, 4]})
      sorted_df = evaluator.solve(command="${__df}.sort_values('col2', ascending=False)", df=df)  #    col1  col2
                                                                                                     0     2     4
                                                                                                     1     1     3
      ```

4. Supported operations
   - in is not supported yet
   - comparation (<=, <, \> , \>=, !=, ==)
   - unary (\+, \-)
   - boolean (~, &, |, ^)
   - binary (\+, \-, /, \*, //, %, **)

5. Supported functions
   - map, filter, list, range
   - bool, int, float, complex, str
   - numpy module functions (np.mean, etc.)
   - pandas module functions (pd.date_range, etc.)
   - anonymous functions

6. Supported access to data
   - ${col_name} is same as df['col_name']
   - ${__df} is same as df

7. It is possible to use your own class for preprocessing or calculating
    -  ```
       from safe_evaluation import Evaluator, BasePreprocessor
       from safe_evaluation.constants import TypeOfCommand

       class MyPreprocessor(BasePreprocessor):
           def __init__(self, evaluator):
               self.evaluator = evaluator
   
           def prepare(self, command, df, local):
               return [(TypeOfCommand.VARIABLE, 'v'), '**', (TypeOfCommand.VALUE, 2), '>', (TypeOfCommand.VALUE, 5)]
   
   
       evaluator = Evaluator(preprocessor=MyPreprocessor)
   
       expression = 'v ** 2 > 5'
   
       output = evaluator.solve(expression, local={'v': 2})    #    False
       ```

8. It is possible to use your own settings
    -  ```
       from safe_evaluation import Evaluator, Settings
       
       evaluator = Evaluator()
       settings = Settings(allowed_funcs=['filter', 'list'])
       evaluator.change_settings(settings)

       output = evaluator.solve("list(filter(lambda x: x < 0, [-1,0,1]))")   #    [-1]
       ```
       
    -  ```
       from safe_evaluation import Evaluator, Settings
       
       evaluator = Evaluator()
       settings = Settings(allowed_funcs=['list'])
       evaluator.change_settings(settings)

       output = evaluator.solve("list(filter(lambda x: x < 0, [-1,0,1]))")   #    Exception: Unsupported function filter
       ```