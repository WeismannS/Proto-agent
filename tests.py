from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
def test(func) :
    def wrapper(*args,**kwargs) :
        print("Result for current directory:")
        result = func(*args, **kwargs)
        print('\t-'.join((result.split("-") )))
    return wrapper


test_get_files_info = test(get_files_info)
if __name__ == "__main__" :
    # (test_get_files_info("calculator", "."))
    # (test_get_files_info("calculator", "pkg"))
    # (test_get_files_info("calculator", "/bin"))
    # (test_get_files_info("calculator", "../"))
    print(get_file_content("calculator", "main.py"))
    print(get_file_content("calculator", "pkg/calculator.py"))
    print(get_file_content("calculator", "/bin/cat"))
    print(get_file_content("calculator", "pkg/does_not_exist.py"))
    print(get_file_content("calculator", "lorem.txt"))