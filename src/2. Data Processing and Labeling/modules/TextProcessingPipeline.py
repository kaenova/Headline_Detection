from typing import Callable, Optional

class TextProcessingPipeline:
    """
    A text preprocessing pipeline that will run a text to the registered function 
    """
    processor_func: list[Callable[[str], str]] = []
    
    def  __init__(self, processor: Optional[list[Callable[[str], str]]]) -> None:
        self.processor_func = processor
        TextProcessingPipeline.test_processor(self.processor_func)
            
    def process_text(self, text: str) -> str:
        processed_text = text
        for processor in self.processor_func:
            processed_text = processor(processed_text)
        return processed_text
    
    def add_processor(self, func: Callable[[str], str]):
        new_processor = self.processor_func
        new_processor.append(func)
        TextProcessingPipeline.test_processor(new_processor)
        
    @staticmethod
    def test_processor(processor_funcs: list[Callable[[str], str]]):
        dummy_text = "Lorem ipsum dayeuh kolot"
        
        processed_text = dummy_text
        for processor in processor_funcs:
            processed_text = processor(dummy_text)
            if type(processed_text) != str:
                raise TypeError(f"{processor} doesn't have an output of str type")
    
# Example on how to use it        
if __name__ == "__main__":
    def change_to_a(text: str) -> str:
        return "a"
    
    def change_to_b(text:str) -> str:
        return "b"
    
    def change_to_c(text:str) -> str:
        return "c"
    
    dummy_text = "this is a dummy text"
    
    # Instantiate processor and register change_to_a and change_to_b
    processor = TextProcessingPipeline([change_to_a, change_to_b])
    print("Stage 1 Text:", processor.process_text(dummy_text)) # Output: Stage 1 Text: b
    
    # Adding more processor change_to_c
    processor.add_processor(change_to_c)
    print("Stage 2 Text:", processor.process_text(dummy_text)) # Output: Stage 2 Text: c