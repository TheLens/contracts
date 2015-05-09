import os
import subprocess


def download_attachment_file(bidno, bidfilelocation):
        if not os.path.exists(bidno):
            p = subprocess.Popen([
                'curl',
                '-o',
                bidfilelocation,
                'http://www.purchasing.cityofno.com/bso/external/document/' +
                'attachments/attachmentFileDetail.sdo',
                '-H',
                'Pragma: no-cache',
                '-H',
                'Origin: null',
                '-H',
                'Accept-Encoding: gzip,deflate,sdch',
                '-H',
                'Accept-Language: en-US,en;q=0.8',
                '-H',
                'Content-Type: multipart/form-data; ' +
                'boundary=----WebKitFormBoundaryP4a4C1okQYkBGBSG',
                '-H',
                'Accept: text/html,application/xhtml+xml,' +
                'application/xml;q=0.9,image/webp,*/*;q=0.8',
                '-H',
                'Connection: keep-alive',
                '--data-binary',
                '''------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="mode"\r
\r
download\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="parentUrl"\r
\r
/external/purchaseorder/poSummary.sdo\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="parentId"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="fileNbr"\r
\r
''' + bidno + '''\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="workingDir"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="docId"\r
\r
4051927411\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="docType"\r
\r
P\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="docSubType"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="releaseNbr"\r
\r
0\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="downloadFileNbr"\r
\r
''' + bidno + '''\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="itemNbr"\r
\r
0\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="currentPage"\r
\r
1\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="querySql"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="sortBy"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="sortByIndex"\r
\r
0\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="sortByDescending"\r
\r
false\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="revisionNbr"\r
\r
0\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="receiptId"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="vendorNbr"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="vendorGrp"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="invoiceNbr"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="displayName"\r
\r
Grainger Inc. Februaryl 2008.pdf\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG--\r
''',
                '--compressed'
            ])
            p.wait()
