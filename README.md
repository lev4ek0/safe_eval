# save_evaluation

save_evaluation - is an implementation of polish notation algorithm for mathematical and dataframe operations

# how to use

1. Installation
    ```
    pip install safe-evaluation
    ```
2. Tutorial 
   - import evaluation method
    ```
    from save_evaluation import solve_expression
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

4. Supported operations
   - in is not supported yet
   - comparation (<=, <, \> , \>=, !=, ==)
   - unary (\+, \-)
   - boolean (~, &, |, ^)
   - binary (\+, \-, /, \*, //, %, **)

5. Supported functions
   - map, filter, list, range
   - np module functions (np.mean, etc.)
   - anonymous functions
