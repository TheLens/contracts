
'''
Maintains an archive of the DocumentCloud projects on S3.

Does not perform one-item backups or retrieve files from the city.
It only pulls down what is already in the DocumentCloud projects.

This is a slow process, so it is only run one time per day (at night).

TODO: Move all DocumentCloud interaction to document_cloud.py and database
interaction to db.py.
'''

import os
import re
import boto
from boto.s3.connection import OrdinaryCallingFormat
from pythondocumentcloud import DocumentCloud

from scripts.slack import Slack
from scripts.db import Db


class Archive(object):
    '''Methods for syncing DocumentCloud projects with S3 archive.'''

    def __init__(self):
        self.s3_dir = 'contracts/document-cloud-archive'

        self.client = DocumentCloud(
            os.environ.get('DOCUMENT_CLOUD_USERNAME'),
            os.environ.get('DOCUMENT_CLOUD_PASSWORD'))

        conn = boto.s3.connect_to_region(
            'us-west-2',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            calling_format=OrdinaryCallingFormat())

        self.bucket = conn.get_bucket(
            'projects.thelensnola.org', validate=False)

    def test_credentials(self, document_cloud_id):
        doc = self.client.documents.get(document_cloud_id)
        print doc.id

    def main(self):
        '''Loop through DocumentCloud projects and sync them.'''

        for project in self.client.projects.all():
            self.sync_archive_with_project(project)

    def sync_archive_with_project(self, project):
        '''Syncs DocumentCloud project with S3.'''

        for document_id in self.get_unarchived_list(project):
            print 'Document ' + document_id
            self.copy_to_s3(document_id, project)

    def get_unarchived_list(self, project):
        '''Finds documents on DocumentCloud that have not been archived.'''

        archived_set = set(self.get_archived_list(project))

        print 'Getting project list from DocumentCloud...'
        project_set = set(self.get_project_list(project))
        print 'Done.'

        missing_from_archive = project_set - archived_set

        return list(missing_from_archive)

    def get_archived_list(self, project):
        '''Gets the list of .pdf files in this project's archive folder.'''

        file_list = []
        file_dir = "%s/%s" % (self.s3_dir, project.id)

        for key in self.bucket.list(prefix=file_dir):
            if key.name.endswith('.pdf'):
                filename = key.name.split('/')[-1].split('.')[0]
                file_list.append(filename)

        return file_list

    def get_project_list(self, project):
        '''Queries DocumentCloud projects for lists of purchase orders.'''

        # Takes ~45 minutes to retrieve
        document_list = self.client.projects.get(id=project.id).document_list

        document_cloud_ids = []

        for document in document_list:
            # Backup DB for DocumentCloud project metadata
            metadata = self.get_metadata(document, project)
            Db().update_or_add_to_archive(metadata)

            try:
                document_cloud_ids.append(document.id)
            except KeyError:  # If 'purchase order' field is missing
                pass

        return document_cloud_ids

    def alert_possible_ssn(self, document_cloud_id, matching_string):
        '''Sends notice to remove this file from DocumentCloud.'''

        # Don't automate this. Send alert, then manually delete in case wrong.
        Slack().send_ssn_notice(document_cloud_id, matching_string)

    def copy_to_s3(self, document_cloud_id, project):
        '''Uploads file to S3 archive.'''

        # Grab OCR'd text.
        source_text = self.client.documents.get(document_cloud_id).full_text
        destination_text = '%s/%s-%s/text/%s.txt' % (
            self.s3_dir, project.id, project.title, document_cloud_id)

        # Searches entire OCR'd text for SSNs.
        ssn_re1 = re.compile(r'[0-9]{3}-[0-9]{2}-[0-9]{4}')
        ssn_re2 = re.compile(r'[0-9]{9}')
        ssn_re3 = re.compile(r'ssn')

        has_ssn = (ssn_re1.search(source_text.lower()) or
                   ssn_re2.search(source_text.lower()) or
                   ssn_re3.search(source_text.lower()))

        if has_ssn:  # A match
            matching_string = has_ssn.group(0)  # TODO: Will this always work?
            self.alert_possible_ssn(document_cloud_id, matching_string)

            # TODO: Add to skip-list.csv.
            return

        print "Uploading to S3..."

        # Create copies of PDFs
        source_pdf = self.client.documents.get(document_cloud_id).pdf
        destination_pdf = '%s/%s-%s/pdfs/%s.pdf' % (
            self.s3_dir, project.id, project.title, document_cloud_id)

        # Create copies of document images
        source_large_image = self.client.documents.get(
            document_cloud_id).large_image
        destination_large_image = '%s/%s-%s/large_image/%s.gif' % (
            self.s3_dir, project.id, project.title, document_cloud_id)

        # Send PDFs, text and images to S3
        pdf_key = boto.s3.key.Key(self.bucket)
        pdf_key.key = destination_pdf
        pdf_key.set_contents_from_string(source_pdf)

        text_key = boto.s3.key.Key(self.bucket)
        text_key.key = destination_text
        text_key.set_contents_from_string(source_text)

        large_image_key = boto.s3.key.Key(self.bucket)
        large_image_key.key = destination_large_image
        large_image_key.set_contents_from_string(source_large_image)

    def get_metadata(self, doc, project):
        '''Return the metadata associated with a DocumentCloud contract.'''

        metadata = {}

        # DocumentCloud-provided metadata
        metadata['access'] = doc.access
        # metadata['annotations'] = doc.annotations
        metadata['canonical_url'] = doc.canonical_url
        metadata['contributor'] = doc.contributor
        metadata['contributor_organization'] = doc.contributor_organization
        metadata['created_at'] = doc.created_at
        metadata['description'] = doc.description
        metadata['document_cloud_id'] = doc.id
        metadata['document_title'] = doc.title
        # metadata['entities'] = doc.entities
        metadata['full_text_url'] = doc.full_text_url
        metadata['large_image_url'] = doc.large_image_url  # 1st page only
        # metadata['mentions'] = doc.mentions
        metadata['normal_image_url'] = doc.normal_image_url
        metadata['number_of_pages'] = doc.pages
        metadata['pdf_url'] = doc.pdf_url
        metadata['project_id'] = str(project.id)
        metadata['project_title'] = project.title
        metadata['published_url'] = doc.published_url
        metadata['related_article'] = doc.related_article
        # metadata['sections'] = doc.sections
        metadata['small_image_url'] = doc.small_image_url
        metadata['source'] = doc.source
        metadata['thumbnail_image_url'] = doc.thumbnail_image_url
        metadata['updated_at'] = doc.updated_at

        # Additional, custom metadata
        metadata['contract number'] = self.get_value(doc, 'contract number')
        metadata['department'] = self.get_value(doc, 'department')
        metadata['purchase order'] = self.get_value(doc, 'purchase order')
        metadata['vendor'] = self.get_value(doc, 'vendor')
        metadata['vendor_id'] = self.get_value(doc, 'vendor_id')

        return metadata

    def get_value(self, document, attribute):
        '''
        Gets additional, custom metadata from DocumentCloud documents,
        if it exists.
        '''

        try:
            value = document.data[attribute]
            if value == '':
                value = None
            elif value == 'unknown':
                value = None

                # Correct and update DocumentCloud metadata
                document.data[attribute] = ''
                document.put()

            return value
        except KeyError:
            return None

if __name__ == '__main__':
    Archive().main()
    # Archive().test_credentials(
    #     '2671487-REDMELLON-LLC-Original-contract-to-provide-472')
