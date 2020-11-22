# pyGrowthSimilarityAnalysis
CUDA accelerated script that will compare one or more functions to a baseline one and will pick the function(s) with the most similar growth rate. The baseline and test functions must return a numerical value for this script to work.


### Language: ### 

- Tested in Python 3.8.6, should work in all Python 3.7+ versions.


# Installation

- Download the repository

- Install the requirements in the requirements.txt file (pip install -r requirements.txt)

# Usage

Start by opening the **TestFunctions.py** file, where you will declare all your test functions. Each function must return a numerical value and take exactly one regular argument, and the **kwargs argument. Here's an example of a valid function in the TestFunctions.py file:

![alt text](https://i.imgur.com/eZPeJzH.png)

 

You must also declare a dictionary called **MAP_FUNCTIONS_DICT**. This dictionary will serve as a mapping for each test function you declare. Here's an example:

![alt text](https://i.imgur.com/HtCBNcO.png)

- The main dictionary key is the name of your test function.

- The **name** parameter is the name of the function that will appear on the final rendered graph.

- The **nameSuffix** parameter is anything you would like to add as a suffix to the **name** parameter. Notice here the identifier **\_\_variable\_**. This identifier is followed by a valid variable name in scope when in the main loop.

- The **kwargs** parameter is the kwargs that will be passed to your test functions. Each value support the identifier **\_\_variable\_**

 

You can now open the **main.py** file. You will need to transfer the function you want to test inside the **baselineFunction** function. Again, this function must have one regular parameter, and the **kwargs parameter:

![alt text](https://i.imgur.com/48ZWU8t.png)

 

Once it's done, all that's left is to set your desired main loop parameters:

![alt text](https://i.imgur.com/GbBhu89.png)

 
 
 
 
You can now run the script. Here's an example of output, where the most similar function is n^2 * c, where c = 2:
![alt text](https://i.imgur.com/5mELB0v.png)
![alt text](https://i.imgur.com/ds63Mvs.png)
