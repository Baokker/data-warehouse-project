# data-warehouse-project

# 说明

同济大学软件学院2022年秋数据仓库课程项目

项目结构:

```
.
├── README.md
├── data-process # 爬虫 pandas数据混乱（较为混乱）
├── data-warehouse-backend # 项目后端（flask）
├── data-warehouse-frontend # 项目前端（仿照vue-admin-template）
├── 数据仓库项目报告.assets # 图片
├── 数据存储设计说明.assets # 图片
├── 数据仓库项目报告.md # 两份报告
└── 数据存储设计说明.md
```

# git submodule

本项目涉及多个Git项目 故采用submodule进行管理

使用时

```
git clone https://github.com/Baokker/data-warehouse-project.git # clone
git submodule init # 初始化（一次即可）
git submodule update # 更新
```

# 更多..

见我的[Blog教程](https://baokker.github.io/2022/12/17/%E6%95%B0%E6%8D%AE%E4%BB%93%E5%BA%93%E8%AF%BE%E7%A8%8B%E9%A1%B9%E7%9B%AE%E7%BB%8F%E9%AA%8C%E5%BF%83%E5%BE%97/)，除了readme的内容外，还重点更新了

- Spark的配置
- pandas的使用心得
- 前后端对接

等等心得
