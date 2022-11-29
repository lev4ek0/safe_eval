# safe_evaluation

safe_evaluation - is an implementation of polish notation algorithm for mathematical and dataframe operations

# how to use

1. Installation
    ```
    pip install safe-evaluation
    ```
2. Tutorial 
   - import evaluation method
    ```
    from safe_evaluation import solve_expression
    ```
   - send string that you want to evaluate
    ```
    result = solve_expression(command="2 + 2")
    ```
   - method will return result
    ```
    print(result)
    ```
3. Examples of usage
   -  ```
      solve_expression(command="2 + 2")  # 4
      ```
   -  ```
      solve_expression(command="lambda x: x * 2")  # lambda x: x * 2
      ```
   -  ```
      solve_expression(command="2 * x - y", local={"x": 2, "y": 3})  # 1
      ```

   -  ```
      import pandas as pd

      df = pd.DataFrame(data={'col1': [1, 2], 'col2': [3, 4]})
      solve_expression(command="${col1} + ${col2}", df=df)  # 0   4
                                                              1   6
                                                              dtype: int64
      ```
   -  ```
      solve_expression(command="list(map(lambda x, y: x * 2 + y, range(5), range(3, 8)))")  # [3,6,9,12,15]
      ```
   -  ```
      solve_expression(command="list(map(lambda x: x + y, [0,1,2,3,4]))", local={"y": 10})  # [10,11,12,13,14]
      ```
   -  ```
      import pandas as pd
     
      df = pd.DataFrame(data={'col1': [1, 2, 4, 7], 'col2': [3, 4, 8, 9]})
      solve_expression(command="np.mean(${col1}) + np.mean(${col2})", df=df)  # 9.5
      ```
   -  ```
      import pandas as pd
     
      df = pd.DataFrame(data={'col1': [1, 2, 4, 7], 'col2': [3, 4, 8, 9]})
      solve_expression(command="${col1}.apply(lambda v: v ** 2 > 0).all()", df=df)  # True
      ```
   -  ```
      import pandas as pd
     
      df = pd.DataFrame(data={'col1': [1, 2, 4, 7], 'col2': [3, 4, 8, 9]})
      solve_expression(command="${col1}.apply(lambda v: 1 if v < 3 else 2)", df=df)  # 0    1
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
      solve_expression(command="${dates}.dt.dayofweek", df=df)  # 0    4
                                                                  1    5
                                                                  2    6
                                                                  3    0
                                                                  4    1
                                                                  5    2
                                                                  6    3
                                                                  Name: dates, dtype: int64
      ```
   -  ```
      range = solve_expression(command="pd.date_range(start='2021-02-05', end='2021-03-05', freq='1D')"")
      len(range)  # 29
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
