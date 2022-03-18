class VMWriter:
    def __init__(self):
        self.VM = []

    def write(self, line):
        self.VM.append(line + '\n')

    def write_int(self, num):
        num = str(num)
        self.VM.append('push constant ' + num + '\n')

    def write_string(self, string):
        self.write_int(len(string))
        self.write_call('String', 'new', 1)
        for c in string:
            self.write_int(ord(c))
            self.write_call('String', 'appendChar', 2)

    def write_call(self, caller, func, argnum):
        self.VM.append(f'{caller}.{func} {argnum}\n')

    def write_if(self, label):
        self.VM.append(f'not\n')
        self.VM.append(f'if-goto {label}\n')

    def write_label(self, label):
        self.VM.append(f'label {label}\n')

    def write_function(self, funcClass, funcName, localVarNum):
        self.VM.append(f'function {funcClass}.{funcName} {localVarNum}')