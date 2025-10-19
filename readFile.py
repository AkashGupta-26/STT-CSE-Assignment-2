import re
from typing import Tuple


class SourceCodeProcessor:
    """Handles reading and preprocessing C source files"""
    
    @staticmethod
    def loadSourceFromFile(filePath: str) -> str:
        """Load complete source code from a C file"""
        try:
            with open(filePath, "r", encoding="utf-8") as fileHandle:
                return fileHandle.read()
        except FileNotFoundError:
            raise ValueError(f"Source file not found: {filePath}")
    
    @classmethod
    def cleanSourceCode(cls, rawSource: str) -> str:
        """Remove comments and preprocessor directives from source"""
        # Strip block comments
        processedSource = re.sub(r"/\*.*?\*/", "", rawSource, flags=re.DOTALL)
        # Strip line comments
        processedSource = re.sub(r"//.*", "", processedSource)
        
        cleanedLines = []
        for codeLine in processedSource.splitlines():
            if codeLine.lstrip().startswith("#"):
                cleanedLines.append("")  # Replace preprocessor lines with empty lines
            else:
                cleanedLines.append(codeLine)
        
        return "\n".join(cleanedLines)
    
    @classmethod
    def locateMainFunction(cls, sourceCode: str) -> Tuple[int, int]:
        """Find the boundaries of the main function in source code"""
        # Try to match standard main function signatures
        mainPattern = re.search(r"\bint\s+main\s*\([^)]*\)\s*\{", sourceCode)
        if not mainPattern:
            mainPattern = re.search(r"\bmain\s*\([^)]*\)\s*\{", sourceCode)
        
        if not mainPattern:
            raise ValueError("Main function signature not detected in source")
        
        # Find opening brace position
        bracePosition = sourceCode.find("{", mainPattern.end() - 1)
        if bracePosition == -1:
            raise ValueError("Invalid main function structure: missing opening brace")
        
        # Track brace nesting to find matching closing brace
        nestingLevel = 0
        currentPos = bracePosition
        
        while currentPos < len(sourceCode):
            character = sourceCode[currentPos]
            if character == '{':
                nestingLevel += 1
            elif character == '}':
                nestingLevel -= 1
                if nestingLevel == 0:
                    return (bracePosition + 1, currentPos)
            currentPos += 1
        
        raise ValueError("Invalid main function structure: missing closing brace")
    
    @classmethod
    def extractMainBody(cls, sourceCode: str) -> Tuple[str, int]:
        """Extract the body of main function and calculate starting line number"""
        beginIndex, endIndex = cls.locateMainFunction(sourceCode)
        functionBody = sourceCode[beginIndex:endIndex]
        lineNumber = sourceCode[:beginIndex].count("\n") + 1
        return functionBody, lineNumber
