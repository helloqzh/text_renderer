#!/bin/bash
# 生成十万张图片到lmdb
# python main.py --num_img 100000 --mongo --mongo_connection_url "mongodb://localhost" --mongo_db kbw --mongo_collection jiji --mongo_field article --viz --lmdb
# 预览
# python main.py --viz --mongo --mongo_connection_url "mongodb://localhost" --mongo_db kbw --mongo_collection jiji --mongo_field article --num_img 3