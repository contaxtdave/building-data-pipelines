class DataPipeline():
    first_tool = "AirFlow"

datapipeline = DataPipeline()
print(datapipeline.first_tool)

# Parent class
class DataPipelineBook:
    def __init__(self):
        print("This book is very hot in the market")
        self.pages = 300
    
    def what_is_this(self):
        print("Book")

    def pages(self):
        return self.pages
    
# Child class
class PythonDataPipelineBook(DataPipelineBook):
    def __init__(self):
        super().__init__()
        print("Create Data Pipeline with Python") 

    def what_technology_is_used(self):
        return "Python"
    
pipeline = PythonDataPipelineBook()
print(pipeline.what_is_this())
print(pipeline.what_technology_is_used())
print(pipeline.pages)
