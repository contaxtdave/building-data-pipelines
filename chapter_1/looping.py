# for loop
# Program to return a list of even number from a give list

# Given list
numbers = [7, 4, 3, 5, 8, 9, 8, 6, 14]

# Declare an empty list 
even_numbers = []

# iterate over the list 
for num in numbers:
    if num % 2 == 0:
        even_numbers.append(num)

print("The Even number list is: ", even_numbers)

# while loop 
count = 0

while (count < 11):
    print("The current number is: ", count)
    count += 1

print("While loop terminates here.")
