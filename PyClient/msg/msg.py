from abc import ABC,abstractmethod
class msg(ABC):
    @abstractmethod
    def read(self,json):
        pass
    @abstractmethod
    def write(self,json):
        pass

class handle(ABC):
    @abstractmethod
    def handle(self,msg,context):
        pass
