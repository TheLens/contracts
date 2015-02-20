#!/bin/bash
#The main summary finder for city contracts
curl 'http://www.purchasing.cityofno.com/bso/external/publicContracts.sdo' -H 'Pragma: no-cache' -H 'Origin: http://www.purchasing.cityofno.com' -H 'Accept-Encoding: gzip,deflate,sdch' -H 'Accept-Language: en-US,en;q=0.8' -H 'Content-Type: application/x-www-form-urlencoded' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: no-cache' -H 'Referer: http://www.purchasing.cityofno.com/bso/external/publicContracts.sdo' --data 'status=&mode=sort&currentPage=1&querySql=%5BPROCESSED%5Dc%3A5f%3A2%3A61%3A58%3A-62%3A7%3A3%3A9%3A2d%3A71%3A30%3A-62%3A3f%3A-6f%3A-75%3A-58%3A7c%3A4%3A-12%3A5b%3A5e%3A45%3A46%3A44%3A14%3A-69%3A-30%3A79%3A1f%3A-39%3A-46%3A38%3A-19%3A4d%3A-77%3A1%3A44%3A37%3A9%3A-4d%3A-77%3A-6c%3A-c%3A-35%3Aa%3A5d%3A-39%3A-7f%3A-73%3A-5a%3A-47%3A46%3A5b%3A-14%3A78%3A63%3A3f%3A43%3A-60%3A-7c%3A7e%3A37%3A70%3Af%3A73%3A37%3A6b%3A47%3A42%3A46%3A58%3A77%3A-6a%3A-11%3A-2e%3A64%3A-3d%3A-3b%3A59%3A-34%3A2d%3A57%3A-41%3A5%3A-7%3A-71%3A-6d%3A3e%3A56%3A64%3A5d%3A67%3A77%3A-6e%3A-b%3A67%3A7d%3A-2e%3A2a%3A-3e%3A65%3A26%3A-17%3A-62%3A3%3A1f%3A-5e%3A2f%3A-74%3A2b%3A-4f%3A1e%3A73%3A2f%3A4f%3A-5b%3A78%3A-22%3A25%3A34%3A5f%3A-21%3A6c%3A-2b%3A3e%3A-5a%3A51%3A-13%3A12%3A-40%3A7f%3A-3%3A-7%3A48%3A-56%3A-47%3A-6%3A-34%3A19%3A6%3A5%3A3d%3A-75%3A-25%3A58%3A-60%3A1d%3A11%3A-18%3A-60%3A61%3A-12%3A15%3A6%3A5b%3A60%3A73%3A17%3A-57%3A6d%3A-60%3A-3f%3A-29%3A-39%3A-51%3A-24%3A-1d%3A-1b%3A-57%3A7e%3A6f%3A1a%3A-8%3A-4a%3A8%3A3a%3A1b%3A-3f%3A-15%3A-75%3A-e%3A-42%3A-4%3A-27%3A-2%3A-43%3A-2e%3A-20%3A-5c%3A-3e%3A-50%3A-3d%3A16%3A-4c%3A7e%3A-64%3A-4%3A-3%3A-77%3A32%3A53%3A-8%3A43%3A10%3A-4f%3A69%3A-57%3A2f%3A-6c%3A-46%3A0%3A25%3A-78%3A-3d%3A56%3A17%3A-f%3A-6d%3A-49%3A7a%3A-6e%3A14%3A-13%3A18%3A-1b%3A-2c%3A5c%3A-49%3A-26%3A17%3A-3c%3A3d%3A-4e%3A-34%3A-23%3A-3f%3A-71%3A-33%3A1b%3A-40%3A37%3A-6a%3A-47%3A16%3A36%3A-16%3A-9%3A-32%3A-1c%3A53%3A-1%3A22%3A-59%3A-13%3A1c%3A7b%3A17%3A8%3A50%3A-37%3A-45%3A-1f%3A-7%3A49%3A3b%3A58%3Aa%3A1%3A-e%3A-5c%3A1e%3A57%3A1%3A-73%3A69%3A-5%3A3%3A8%3A62%3A-52%3A-42%3A34%3A43%3A-39%3A5f%3A-17%3Ad%3A3e%3A-3b%3A3d%3A-3d%3A-45%3A43%3A9%3A1c%3A-5%3A3d%3A-c%3A-63%3A2d%3A-1d%3A62%3A-5b%3A68%3A-46%3A4c%3A-b%3A-57%3A-70%3A45%3A5b%3A-57%3A1b%3A-5e%3A-79%3A2a%3A49%3A-a%3A-47%3A37%3A-1a%3Ab%3A-62%3A69%3A-18%3A-9%3A-5b%3A27%3A-4e%3A5d%3A-66%3A4b%3A2e%3A29%3A-7c%3A13%3A56%3A7b%3A12%3A34%3A6f%3A31%3A-19%3A6b%3A-2c%3A18%3Ac%3A7d%3A44%3A26%3A-66%3A3a%3A22%3A4f%3A-7%3A-15%3A2d%3A-7b%3A-2b%3A-19%3A-63%3A8%3A-7f%3A75%3A-42%3A60%3A3c%3A42%3A-5%3A2d%3A58%3A62%3A44%3A-38%3A10%3A17%3A72%3A-48%3A4e%3A18%3A6%3A7a%3A-40%3A77%3A-37%3A11%3Af%3A-12%3Ab%3A-1d%3A57%3A-6%3A65%3A40%3A4c%3A1e%3A6c%3A-74%3A47%3A-42%3A-64%3A49%3A-6f%3A-4d%3A40%3A7f%3A54%3A-46%3A-1f%3A45%3A44%3A-6b%3A-13%3A-71%3A-3c%3A48%3A-12%3A11%3A-7c%3A4c%3A-78%3A-5c%3A-53%3A42%3A79%3A-30%3A1b%3A2d%3A56%3A8%3A59%3A-10%3A-5e%3A3d%3A-2a%3A77%3A-42%3A-17%3A2e%3A4d%3A3c%3A-23%3A-72%3A-1a%3A-14%3A-77%3A-17%3A-69%3A2e%3A-1a%3A-45%3A-45%3A-4c%3A-64%3A2d%3A60%3A2%3A-73%3A55%3A-36%3A39%3A-33%3A-5b%3A-15%3A-36%3A2d%3A3%3A29%3A-65%3A63%3A23%3A43%3A-23%3A-20%3A9%3A33%3A-2%3A29%3A-26%3A57%3A16%3A-4%3A-1e%3A-49%3A-71%3A-3b%3A-4d%3A-46%3A-72%3A-25%3A40%3A-44%3A-1a%3A1b%3A2f%3A26%3A-34%3Ab%3A14%3Af%3A-35%3A-66%3A-60%3A20%3A-58%3A57%3A6a%3A-59%3A-4c%3A-73%3A12%3A-4e%3A-40%3A67%3A-54%3A-6f%3A66%3A5a%3A-b%3A-11%3A-49%3A46%3A-1a%3A-26%3A44%3A-3a%3A-44%3A-1e%3A3b%3A3d%3A5f%3A43%3A2f%3A-3d%3A-6e%3A-38%3A51%3A54%3A-3d%3A6c%3A-2f%3A7%3A4c%3A-15%3A32%3A-2b%3A72%3A-5b%3A6d%3A-65%3A4c%3A-3%3A16%3A-67%3A5a%3A63%3A-65%3A47%3A-5c%3A12%3A-1c%3A-61%3A2f%3A69%3A51%3A-54%3A-4a%3A-70%3A28%3A-52%3A14%3A-2f%3A4d%3A-5f%3A-79%3A-44%3Af%3A-7f%3A-6%3A-30%3A27%3A-8%3A56%3A-7b%3A48%3A3c%3A52%3A-6e%3A3e%3A-44%3A14%3A-47%3A6d%3A-1a%3A29%3A30%3A-4a%3Ab%3A5c%3A-71%3A44%3A-d%3A23%3A-c%3A-32%3A7b%3A-4b%3A24%3A-4d%3A7b%3A-4e%3A73%3A-3e%3A-23%3A-3c%3A-54%3A-47%3A26%3A7f%3A1b%3A68%3A-77%3A2c%3A-37%3A-1%3A-72%3A-5a%3A25%3A11%3Aa%3A-22%3A2e%3A-46%3A11%3A7d%3A-19%3A-34%3A7b%3A-20%3A-3e%3A-6f%3A-67%3A-1f%3A24%3A2c%3A53%3A52%3A-1a%3A-10%3A47%3A6%3A-61%3A21%3Ae%3A-50%3A31%3A35%3Ac%3A11%3A-3d%3A-4b%3A20%3A-10%3A-1e%3A-35%3A-25%3A1c%3A3a%3A-40%3A6a%3A3b%3A-17%3A-3c%3A-17%3A3f%3A-1%3A39%3A47%3A0%3A-76%3A-10%3A76%3A-6a%3A4c%3A-64%3A2a%3A6c%3A-25%3A56%3A-8%3A-2f%3A38%3A70%3A-7e%3A-1d%3A2e%3A-15%3A-4c%3A-a%3A6b%3A-34%3A-34%3A-26%3A-49%3A-16%3A1e%3Ae%3A-71%3A-22%3A-54%3A2c%3A-4c%3A22%3A-19%3A3a%3A-2d%3A3c%3A37%3A-2c%3A-4b%3A33%3A7%3A-14%3A3b%3A77%3A27%3A4b%3A-12%3A-1b%3A-27%3A22%3A-18%3A-16%3A-46%3A2b%3A-38%3A-5b%3A5f%3A-6a%3A19%3A70%3A-49%3A-4%3A-28%3A68%3A-1d%3A-58%3A58%3A51%3A70%3A-70%3A-4f%3A2%3A-4d%3A53%3A5f%3A18%3A5e%3A2%3A31%3A-44%3A47%3A13%3A1a%3A-67%3A-11%3A-1d%3A-77%3A31%3A77%3A-77%3A12%3A-14%3A1%3A-1b%3A38%3A-71%3A-20%3A-b%3A-26%3A-51%3A46%3A-4d%3A-65%3A23%3A18%3A-5a%3A-54%3A-69%3A-10%3A39%3A-38%3A-10%3A21%3A57%3A-6f%3A-b%3A35%3A-4%3A-3f%3A56%3A-49%3A-74%3Ab%3A-a%3A4%3A6d%3A8%3A59%3A-3%3A4c%3A48%3A-58%3A4c%3A-48%3A10%3A-5a%3A67%3A1e%3A-5%3A5c%3A-21%3A17%3A-51%3A-7c%3A72%3A-46%3A-25%3A-73%3A-65%3A4f%3A-7a%3A-27%3A-4b%3A39%3A7%3A62%3A4d%3A-2d%3A-5d%3A3d%3A6d%3Af%3A4b%3A18%3A-24%3A-6b%3A-60%3A-2f%3A21%3A7a%3A6e%3Ad%3A4e%3A-51%3A-60%3Ab%3A-5c%3A7f%3A19%3A10%3A-2%3A66%3A-39%3A-50%3A-47%3A-3c%3A4e%3A-5e%3A-d%3A-58%3A-3%3A26%3A-28%3A41%3A-47%3A-2d%3A-15%3A1c%3A-18%3A3f%3A-4d%3A3c%3A51%3A-7b%3A-72%3A-64%3Ad%3A11%3A-71%3A36%3A4c%3A-21%3A-5c%3A7a%3A7f%3A7f%3A47%3A29%3A-27%3A3%3A-5e%3A-30%3A-72%3A-1%3A-7d%3A4e%3A57%3A-6b%3A-5e%3A5%3A-75%3A-58%3A-14%3A-16%3A-5d%3A-2a%3A6c%3A-42%3A75%3A-26%3A2b%3A17%3A-77%3A-35%3A4a%3A71%3A-1c%3A-f%3A4%3A19%3A28%3A-36%3A-62%3A1c%3A4c%3A-3a%3Ab%3A75%3A-75%3Ad%3A47%3A7a%3A39%3A16%3A-4d%3A-d%3A-11%3A-2f%3A65%3A-66%3A61%3A-34%3A27%3A46%3A-6e%3A74%3Ab%3A56%3A9%3A52%3A1b%3A28%3A45%3A1f%3A-18%3A-44%3A-11%3A-5e%3Aa%3A57%3A51%3A75%3A26%3A2a%3A-31%3A36%3A65%3A55%3A0%3A-78%3A17%3A5c%3A6%3A-6a%3A-2%3A6e%3A-a%3A-b%3A-55%3A77%3A39%3A-42%3A58%3A-43%3A20%3A-78%3A71%3A3%3A13%3A2d%3A3f%3A-56%3A-73%3Ae%3A-38%3A1e&sortBy=beginDate&sortByIndex=5&sortByDescending=true&viewAllFlag=false&activeResult=C&category=&contract%5B0%5D.docId=4051927411&contract%5B1%5D.docId=PW155108&contract%5B2%5D.docId=SD153473&contract%5B3%5D.docId=PD154039&contract%5B4%5D.docId=PM153651&contract%5B5%5D.docId=FC153675&contract%5B6%5D.docId=DI153828&contract%5B7%5D.docId=PW153538&contract%5B8%5D.docId=PM154538&contract%5B9%5D.docId=DI153919&contract%5B10%5D.docId=FC153672&contract%5B11%5D.docId=CA153700&contract%5B12%5D.docId=PM154005&contract%5B13%5D.docId=SD154037&contract%5B14%5D.docId=CI259934&contract%5B15%5D.docId=4051257640&contract%5B16%5D.docId=IG154724&contract%5B17%5D.docId=SD154626&contract%5B18%5D.docId=IG155030&contract%5B19%5D.docId=CI154954&contract%5B20%5D.docId=AV153095&contract%5B21%5D.docId=AV153133&contract%5B22%5D.docId=AV153031&contract%5B23%5D.docId=BC153347&contract%5B24%5D.docId=HS154583' --compressed| grep -o '\bdocId=[A-Z][A-Z][0-9]*&\b' | python /apps/contracts/datamanagement/summaryprocessor.py

mv /apps/contracts/datamanagement*pdf pdfs/

sleep 3h  #give document cloud 3 hours to process the new files. if by some chance it does not finish by then, the sync script will catch them the next time around

python /apps/contracts/datamanagement/lensDocCloudSynch.py

python /apps/contracts/datamanagement/daily_linker.py
python /apps/contracts/datamanagement/emailer.py
python /apps/contracts/datamanagement/backup.py
