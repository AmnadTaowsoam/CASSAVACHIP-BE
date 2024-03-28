# Introduction 
Cassava chip นี้เป็นส่วนที่ให้บริการ การทำนายผลค่าทรายในฝุ่นของมันเส้นที่ใช้ในกระบวนการผลิตอาหารสัตว์ โดยที่ Services นี้ทหน้าที่ในการรับค่าจากฝั่งผู้ใช้งาน(UI)ส่งข้อมูลมาที่ Services นี้แล้วจะทำการส่งผลการทำนายกลับไปที่ ผู้ใช้งาน(UI)

# Getting Started
1.	Installation process
    
    - python environment:

            python -m venv env
            env\scripts\activate

    - Library requirements:

            pip install -r requirements.txt

2.	Software dependencies

        Linux/Ubuntu
        Docker container
        python

3.	Latest releases

        https://betagro-dev@dev.azure.com/betagro-dev/D2023-006-QI-Inspection/_git/CASSAVACHIP-BE

4.	API references

# Build and Test

## Create Images

    docker build -t cassava_serv:latest .

## Run Images

    docker run -d -p 8000:8000 --name cassava_serv cassava_serv:latest


# Contribute
TODO: Explain how other users and developers can contribute to make your code better. 

If you want to learn more about creating good readme files then refer the following [guidelines](https://docs.microsoft.com/en-us/azure/devops/repos/git/create-a-readme?view=azure-devops). You can also seek inspiration from the below readme files:
- [ASP.NET Core](https://github.com/aspnet/Home)
- [Visual Studio Code](https://github.com/Microsoft/vscode)
- [Chakra Core](https://github.com/Microsoft/ChakraCore)