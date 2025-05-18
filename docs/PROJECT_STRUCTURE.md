# 项目文件层级结构

Multi_Collaboration_Framework_Example/
├── docs                
│   ├── INSTRUCTION.md       # 本文件用于规范项目开发的一般操作流程，明确进行开发过程中应遵循的规范。
│   ├── PROJECT_GOALS.md     # 本文件为项目核心目标管理文档，用于分层级、结构化定义项目整体目标，确保团队对「做什么」「做到什么程度」达成共识。
│   ├── PROJECT_STRUCTURE.md
│   └── test.pdf             # 未阅读论文清单（每周更新）
├── Local_Files          # 本地文件存放于此，该文件夹下的文件不会被同步到云端仓库，所以大文件直接放在这里
│   └── .gitignore          
├── Shared_Resources    
│   ├── Data                
│   │   └── Data_Cloud_Drive_Link.md # 用于集中管理数据文件的网盘链接，记录项目/业务相关数据文件的存储位置。 填写格式----数据名称/用途:链接
│   └── Paper                # 参考文献存放处
│       └── .gitkeep            
├── Generate_Project_Hierarchy.py # 用于生成项目文件层级并配置相应文件开头用途注释
└── README.md           