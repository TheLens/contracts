for i in {23..186}
do
   curl -o "$i"'.txt' 'http://www.purchasing.cityofno.com/bso/external/advsearch/searchContract.sdo' -H 'Pragma: no-cache' -H 'Origin: http://www.purchasing.cityofno.com' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: en-US,en;q=0.8' -H 'Content-Type: application/x-www-form-urlencoded' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: no-cache' -H 'Referer: http://www.purchasing.cityofno.com/bso/external/advsearch/searchContract.sdo' -H 'Connection: keep-alive' -H 'DNT: 1' --data 'mode=sort&letter=&currentPage='"$i"'&querySql=%5BPROCESSED%5D5%3A-39%3A62%3A-43%3A64%3A1c%3A69%3A54%3A-2e%3A42%3A5%3A40%3A62%3A29%3A-64%3A-22%3A23%3Af%3A-31%3A6%3A-4d%3A31%3A-71%3A51%3A-5b%3A1a%3A22%3A5b%3A2f%3A2c%3A45%3A-6%3A-11%3A-e%3A-e%3A20%3A55%3A3e%3A21%3A-25%3A6a%3A38%3A-5a%3A-78%3A44%3A-62%3A36%3A-41%3A-7e%3A-43%3A4a%3A-1b%3A7%3A1b%3A0%3A-b%3A43%3A-46%3A34%3A-2b%3A-75%3Ad%3A72%3A-7b%3A-66%3A9%3A40%3A-66%3A-3e%3A-1d%3A-4e%3A7b%3A-73%3Ad%3A-7f%3A53%3A-63%3A2%3A-3%3A-4b%3Aa%3A73%3A-2e%3A68%3A-5c%3A-31%3A-6e%3A-20%3A75%3A-53%3A3b%3A60%3A-32%3A-1%3A-e%3A-14%3A58%3A-2e%3A-12%3A48%3A-39%3A-67%3A54%3A-3f%3A-67%3A6f%3A-57%3A-a%3A-43%3A-41%3A19%3A5a%3A4b%3Ae%3A5b%3A-15%3A5d%3A-12%3A-52%3A-61%3Aa%3A21%3A-3%3A-3c%3A-2%3A6c%3A1c%3A31%3A5d%3A-1f%3A-32%3A2f%3A-19%3A-61%3A-57%3A13%3A-56%3A3c%3A46%3A6e%3A2f%3A-4a%3A-5a%3A-1f%3A-13%3A-14%3A-73%3A-5a%3A66%3A56%3A63%3A30%3A7e%3Aa%3A14%3A18%3Ab%3A8%3A-6f%3A3e%3A-20%3A29%3A3c%3A-42%3A7c%3A2a%3A-67%3A67%3A60%3A-33%3A-79%3A-37%3A-7d%3A-16%3A29%3A5d%3A67%3A52%3A2f%3A3a%3A-c%3A53%3A1%3A-63%3A-56%3A68%3A3d%3A-31%3A-e%3A5b%3A-41%3A6c%3A45%3A2%3A-7f%3A46%3A-a%3A9%3A50%3Ab%3A78%3A-a%3A64%3A29%3A-6b%3A2a%3A-60%3A-72%3A-21%3A10%3A6b%3A5b%3A-74%3A-50%3A-6a%3A2%3A-14%3A2%3A7e%3A22%3A10%3A-7f%3A5e%3A70%3A-d%3A-80%3A29%3A-36%3A5c%3A32%3A9%3A-4%3A55%3A-2b%3A4b%3A-69%3A-5%3A64%3A-40%3A24%3A3a%3A-9%3A-53%3A-67%3A-14%3A5a%3A7b%3A-2a%3A65%3A-33%3A48%3A-76%3A-2e%3A48%3Ac%3A-22%3A2a%3A-68%3A-75%3A-5d%3Ab%3A3d%3A21%3A15%3A-64%3A-6e%3A-54%3A46%3A-56%3A-64%3A41%3A3d%3A5d%3A5c%3A2a%3A3a%3A-4%3A53%3A-43%3A-39%3A4c%3A-6%3A-56%3A-59%3A-68%3A-5d%3A-80%3A47%3A4f%3A35%3A2e%3A-3b%3A-3%3A-25%3A38%3A3c%3A5c%3A1c%3A-4b%3A34%3A-7a%3A-79%3A-4d%3A-16%3A13%3A-56%3A-59%3A-2b%3A23%3A-8%3A1d%3A3e%3A-64%3A52%3A28%3A-c%3A30%3A7e%3A48%3A-3c%3A5e%3A-17%3A35%3A52%3A-34%3A-42%3A22%3A-1%3A-12%3A2f%3A-5b%3A6b%3A42%3A30%3A-2f%3A59%3A6%3A33%3A4a%3A-3b%3A-8%3A-6f%3A-7e%3A4b%3A2b%3A15%3A-4a%3A55%3A-32%3A-3d%3A52%3A8%3A2e%3A72%3A-2d%3A-27%3A2b%3A24%3A4d%3A-67%3A22%3A-54%3A-5f%3A-6e%3A3e%3A1f%3A4c%3A4a%3A68%3A18%3A9%3A-61%3A-40%3A4e%3A-53%3A-58%3A-20%3A4b%3A-19%3A-2d%3A3d%3A-1e%3A7d%3A-3b%3A-72%3A2e%3A-5f%3A-27%3A-39%3Ad%3A-3d%3A12%3A-23%3A-2b%3A1b%3A-71%3A33%3A6%3A56%3A3%3A-2b%3A16%3A-71%3A78%3A-7e%3A-33%3A56%3A-2b%3A-32%3A75%3A19%3A69%3A5d%3A30%3A-8%3A-8%3A3e%3A-13%3A-1d%3A-4d%3A-33%3A7d%3A-6d%3Ad%3A-12%3A3c%3A4b%3A-6c%3A5e%3A7%3A-43%3A4b%3A-5%3A1%3A-75%3A-47%3A-58%3A73%3A37%3A4f%3A-51%3A59%3A-10%3A-61%3A-33%3A-29%3A-31%3A1a%3A-77%3A-3b%3A2c%3A-7b%3A-7e%3A-60%3A7e%3A63%3A-20%3A19%3A-1a%3A-23%3A-2e%3A4d%3A2d%3Ac%3A4a%3A-2%3A56%3A-32%3A-45%3A63%3A-c%3A62%3A-4c%3A13%3A2%3Aa%3A-52%3A-69%3A21%3A-33%3A25%3A2%3A4e%3A76%3A7%3A-4%3A62%3A-69%3A-1%3A-2e%3A5f%3A-1c%3A-71%3A-1%3A-f%3A-25%3A3a%3A-46%3A4f%3A9%3A-45%3A-3d%3A-2b%3A72%3A-68%3A-69%3A73%3A-67%3A7f%3A-4a%3A44%3A-35%3Af%3A52%3A66%3A48%3A65%3A50%3A-4b%3A71%3A9%3A30%3A41%3Af%3A-7d%3A-3%3A-8%3A37%3A-43%3A9%3A-22%3A-46%3A-4d%3A1d%3A2c%3A70%3A-1%3A-4d%3A67%3A56%3A1e%3Ae%3A1e%3A-14%3A49%3A35%3A-46%3A14%3A-64%3A31%3A-4e%3A4f%3A-54%3A75%3A-57%3A-51%3A-2d%3A-2f%3A7f%3A73%3A23%3A-50%3A-1d%3A7c%3A-64%3A-7e%3A64%3A-44%3A40%3A-7c%3A-61%3A-36%3A6c%3A27%3A3%3A-5f%3A36%3A-2c%3A-15%3A1c%3A-71%3Ac%3A-2c%3A41%3A2%3A1d%3A5a%3A-59%3A51%3A1c%3A-28%3A10%3A-16%3A-2d%3A7%3A-31%3A4d%3A-7a%3A-4%3A-37%3A-6d%3A-65%3A-2d%3A-3b%3A-2c%3A-31%3A71%3A7%3A19%3A5b%3A-6b%3A-4f%3A41%3A-4f%3A-33%3A2d%3A-49%3A-7a%3A55%3A18%3A10%3Ad%3Ab%3A-19%3A-1f%3A-1b%3A2e%3A55%3A-7e%3A9%3A-2%3A-52%3A7%3A-4b%3A-6b%3A-36%3A6e%3A-35%3A-5c%3A-1b%3A-f%3A67%3A-46%3A-3b%3A-f%3A14%3A4e%3A62%3A7a%3A6f%3A65%3A7a%3A-2d%3A38%3A-3c%3A-7f%3A6a%3A24%3A-2e%3A-7e%3A-21%3A68%3A5%3A5%3A22%3A-73%3A5%3A60%3A-5f%3A2b%3A-58%3A-3e%3A-76%3A-14%3A-4b%3A-68%3A6e%3A-4%3A6a%3A75%3A5f%3A9%3A-11%3A-4f%3A-5d%3A-67%3A35%3A-43%3A-66%3A5f%3A30%3A-73%3A3c%3A32%3A-55%3A-4%3A-29%3A-73%3A6f%3A6a%3A34%3A1a%3A-e%3A8%3A-15%3A35%3A-4b%3A7a%3A6e%3A-44%3A-29%3A-46%3Aa%3A-1b%3A2f%3A4d%3A-15%3A2b%3A-5f%3A-56%3A-7f%3A-5c%3A-32%3A-5d%3A6e%3A3e%3A-5f%3A-47%3A-a%3A-4%3A53%3A-10%3A-6c%3A64%3A40%3A-1b%3A58%3A-3c%3A-23%3A32%3A-1a%3A7e%3A13%3A50%3A10%3A2f%3A33%3A-6c%3A29%3A6d%3A1d%3A63%3A-29%3A34%3A-b%3A-6%3A-40%3A-a%3A-26%3Ac%3A-16%3A-1e%3A-8%3Aa%3A6b%3A30%3A-63%3A25%3A6e%3Aa%3A-58%3A42%3A-45%3A31%3A26%3A-4%3A-4f%3A17%3A-57%3A75%3A0%3A-54%3A6a%3A-6d%3A79%3A-3%3A-5b%3A1f%3A2c%3A-64%3A2c%3A-2b%3A59%3A50%3A-2e%3A-1%3A1e%3A-36%3A-64%3A2a%3A-7d%3A55%3A-2a%3A-7e%3A56%3A4a%3A38%3Ab%3A-73%3A73%3A5c%3A52%3A10%3A-38%3A-72%3A10%3A-54%3A35%3A-73%3A19%3A-2d%3A-46%3A-c%3A-22%3A24%3A6b%3A1%3A-27%3A-7b%3A-f%3A29%3A-21%3A48%3A-4b%3A33%3A67%3A58%3A62%3A62%3A-76%3A-21%3A7a%3A61%3A-2e%3A3c%3A3f%3A-38%3A-4e%3A-11%3A-31%3A49%3A-1f%3A3e%3A-a%3A-1a%3A-5e%3A-1d%3A-75%3A-35%3A6d%3A78%3A-65%3A77%3A-71%3A1f%3A-23%3A-7e%3A17%3A7f%3A-1a%3A-5%3A70%3A-5b%3A40%3A-13%3A48%3A79%3A2b%3A-6b%3A1d%3A-64%3A77%3A-7%3A72%3A-74%3A-56%3A32%3A7d%3A30%3A-72%3A-5b%3A4f%3A3%3A6f%3A-6e%3A-4b%3A-80%3A-1%3A34%3A5b%3A22%3A-54%3A4b%3A-5a%3A-76%3A-30%3Ab%3A-2%3A3d%3A77%3A5b%3A-50%3A36%3A2e%3A11%3A5%3A5b%3A5d%3A-23%3A64%3A5d%3A15%3A19%3A-56%3A-57%3A16%3A70%3A6%3A-5d%3A-47%3A-78%3A-28%3A-3e%3A-6a%3A72%3A-62%3A-6e%3A-6a%3A-36%3A68%3A6f%3A-46%3A7a%3A-c%3A-40%3A-60%3A-7%3A-5e%3A-7d%3A-21%3A-68%3A25%3A-56%3A-5b%3A-7a%3A47%3A61%3A-3d%3A-42%3A-1a%3A-d%3A-75%3A61%3A-43%3A-56%3A-8%3A43%3A77%3A-24%3A26%3A-58%3A79%3A-74%3A67%3A5%3A-70%3A4f%3A5b%3A31%3A3d%3A47%3A-17%3A7c%3A7f%3A-3d%3A-22%3A-63%3A-42%3A-5a%3A-60%3A10%3A1%3A-27%3A-5e%3A-3b%3A-11%3A-3f%3A2%3A-5a%3A-23%3A-5b%3A-5a%3A-3b%3A74%3A-34%3A-54%3Aa%3A4b%3A5c%3A67%3A55%3A37%3A8%3A-2d%3A-7a%3A-6e%3A-15%3A69%3A-3a%3A77%3A-7a%3A1b%3A-66%3A12%3A1a%3A1b%3A-5b%3A4c%3A-7e%3A5c%3A7%3A14&sortBy=beginDate&sortByIndex=5&sortByDescending=true&masterFlag=true&module=&searchFor=%2Fexternal%2Fadvsearch%2FsearchContract&searchFor=%2Fadvsearch%2FbuyerSearchContract&advancedSearchJspName=%2Fexternal%2Fadvsearch%2FadvancedSearch.jsp&searchAny=false&poNbr=&poTypeParm=&desc=&buyer=&vendorName=&bidNbr=&typeCode=&catalogId=&expireFromDateStr=&expireToDateStr=&itemDesc=&orgId=&departmentPrefix=&classId=&classItemId=&commodityCode=&includeExpired=on' --compressed
   sleep 60  #wait 60 seconds so as not to tax the city server.
done