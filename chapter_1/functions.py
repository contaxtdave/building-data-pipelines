# Functions

def div_of_numbers(num1, num2):
    """This function returns the division of num1 by num2"""
    # This function takes two parameters namely num1 and num 2

    if num2 == 0:
        return "Error: Division by zero is not allowed."
    else:
        return num1 / num2
    
# This is how a python function is called
print(div_of_numbers(8, 0))  # This will print an error message 
print(div_of_numbers(8, 4))  # This will print 2.0
