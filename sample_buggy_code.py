"""Sample buggy code to demonstrate the AI debugger."""

def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    total = 0
    for num in numbers:
        total += num
    # BUG: Division by zero when numbers is empty
    return total / len(numbers)


def process_user_data(user_data):
    """Process user data and return formatted result."""
    # BUG: Accessing undefined variable 'username'
    name = username.strip().title()
    
    # BUG: Potential key error if 'age' doesn't exist
    age = user_data['age']
    
    return f"User: {name}, Age: {age}"


class DataProcessor:
    """A class for processing data."""
    
    def __init__(self):
        self.data = []
    
    def add_item(self, item):
        """Add an item to the data."""
        self.data.append(item)
    
    def get_summary(self):
        """Get a summary of the data."""
        # BUG: AttributeError when data is empty
        return {
            'count': len(self.data),
            'first': self.data[0],  # Index error when empty
            'last': self.data[-1]
        }
    
    def calculate_stats(self):
        """Calculate statistics for numeric data."""
        # BUG: TypeError when data contains non-numeric values
        total = sum(self.data)
        average = total / len(self.data)  # Division by zero
        return {'total': total, 'average': average}


def file_reader(filename):
    """Read and return file contents."""
    # BUG: No error handling for file operations
    with open(filename, 'r') as f:
        content = f.read()
    
    # BUG: Undefined variable 'processed_content'
    return processed_content


if __name__ == "__main__":
    # Examples that would trigger the bugs
    
    # This will cause division by zero
    try:
        avg = calculate_average([])
        print(f"Average: {avg}")
    except ZeroDivisionError as e:
        print(f"Error in calculate_average: {e}")
    
    # This will cause NameError
    try:
        result = process_user_data({'age': 25})
        print(result)
    except NameError as e:
        print(f"Error in process_user_data: {e}")
    
    # This will cause IndexError
    try:
        processor = DataProcessor()
        summary = processor.get_summary()
        print(summary)
    except IndexError as e:
        print(f"Error in get_summary: {e}")
    
    # This will cause FileNotFoundError
    try:
        content = file_reader("nonexistent_file.txt")
        print(content)
    except FileNotFoundError as e:
        print(f"Error in file_reader: {e}")
    except NameError as e:
        print(f"Error in file_reader: {e}")