# -*- coding: utf-8 -*-

'''Create the search results language.

Ex. "10 sales found for keyword 'LLC.'"
'''


class ResultsLanguage(object):

    '''Methods for each page in the app.'''

    def __init__(self, data, number_of_documents):
        '''Starting things off.'''

        self.data = data
        self.number_of_documents = number_of_documents

    def __str__(self):
        return '{0} -- {1.data!s} -- {1.number_of_documents!s}'.format(self.__class__.__name__, self)

    def __repr__(self):
        return '{0}({1.data!r}, {1.number_of_documents!r})'.format(self.__class__.__name__, self)

    def plural_or_not(self):
        '''Checks if more than one result.'''

        if self.number_of_documents == 1:
            plural_or_not = "contract"
        else:
            plural_or_not = "contracts"

        return plural_or_not

    def convert_results_to_text(self, value):
        '''Convert interger to string with commas.'''

        if self.number_of_documents == 0:
            # Skip everything else and return no results language.
            return "No"  # Ex. No contracts found...
        else:
            return "{:,}".format(value)

    def add_initial_language(self, plural_or_not):
        '''Creates initial sentence language.'''

        final_sentence = str(self.convert_results_to_text(
            self.number_of_documents)) + ' ' + plural_or_not + ' found'

        return final_sentence

    def add_keyword_language(self, final_sentence):
        '''Adds keyword or key phrase language.'''

        if self.data['search_input'] != '':
            if len(self.data['search_input'].split()) > 1:
                final_sentence += ' for key phrase "' + \
                    self.data['search_input'] + '"'
                # for 'keyword'
            else:
                final_sentence += ' for keyword "' + \
                    self.data['search_input'] + '"'
                # for 'keyword'

        return final_sentence

    def add_vendors_language(self, final_sentence):
        '''Adds vendor language.'''

        if self.data['vendor'] != '':
            final_sentence += " involving vendor " + self.data['vendor']

        return final_sentence

    def add_departments_language(self, final_sentence):
        '''Adds department language.'''

        if self.data['department'] != '':
            if self.data['vendor'] == '':
                final_sentence += " involving the " + \
                    self.data['department'] + " department"
            elif self.data['vendor'] != '' and self.data['officer'] == '':
                final_sentence += " and the " + self.data['department'] + \
                    " department"
            elif self.data['vendor'] != '' and self.data['officer'] != '':
                final_sentence += ", the " + self.data['department'] + \
                    " department"

        return final_sentence

    def add_officers_language(self, final_sentence):
        '''Adds officers language.'''

        if self.data['officer'] != '':
            if self.data['vendor'] == '' and self.data['department'] == '':
                final_sentence += " involving officer " + \
                    self.data['officer']
            elif self.data['department'] != '':
                final_sentence += " and officer " + self.data['officer']

        return final_sentence

    @staticmethod
    def add_final_sentence_language(final_sentence):
        '''Endings for the sentences.'''

        # Punctuation comes before quotation marks
        if final_sentence[-1] == "'" or final_sentence[-1] == '"':
            last_character = final_sentence[-1]
            final_sentence_list = list(final_sentence)
            final_sentence_list[-1] = '.'
            final_sentence_list.append(last_character)
            final_sentence = ''.join(final_sentence_list)
        else:
            final_sentence += '.'

        return final_sentence

    def main(self):
        '''Runs through all sentence-building methods.'''

        plural_or_not = self.plural_or_not()
        final_sentence = self.add_initial_language(plural_or_not)
        final_sentence = self.add_keyword_language(final_sentence)
        final_sentence = self.add_vendors_language(final_sentence)
        final_sentence = self.add_departments_language(final_sentence)
        final_sentence = self.add_officers_language(final_sentence)
        final_sentence = self.add_final_sentence_language(final_sentence)

        return final_sentence

if __name__ == '__main__':
    pass
