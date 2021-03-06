from hashlib import md5
from kaylee.project import Project, AUTO_PROJECT_MODE
from kaylee.errors import InvalidResultError

class HashCracker(Project):

    def __init__(self, *args, **kwargs):
        super(HashCracker, self).__init__(mode=AUTO_PROJECT_MODE, *args, **kwargs)

        self.alphabet = kwargs['alphabet']
        self.key_length  = kwargs['key_length']
        self.hashes_per_task = kwargs['hashes_per_task']
        self.hash_to_crack = kwargs['hash_to_crack']
        self.salt = kwargs['salt']
        self.client_config.update({
            'md5_script' : kwargs['md5_script'],
            'alphabet' : self.alphabet,
            'key_length' : self.key_length,
            'hashes_per_task' : self.hashes_per_task,
        })

        self.tasks_count = ((len(self.alphabet) ** self.key_length)
                            // self.hashes_per_task + 1)
        self._tasks_counter = 0

    def __getitem__(self, task_id):
        return {
            'id' : task_id,
            'hash_to_crack' : self.hash_to_crack,
            'salt' : self.salt
        }

    def next_task(self):
        if self._tasks_counter < self.tasks_count:
            task = self[self._tasks_counter]
            self._tasks_counter += 1
            return task
        else:
            return None

    def normalize_result(self, task_id, result):
        try:
            key = result['cracked_key']
            test_val = (key + self.salt).encode('utf-8')
            if md5(test_val).hexdigest() == self.hash_to_crack:
                print('here')
                return key
            raise InvalidResultError(result, 'Invalid cracked hash key')
        except KeyError:
            raise InvalidResultError(result, '"cracked_key" was not found in result')

    def result_stored(self, task_id, result, storage):
        if len(storage) == 1:
            # it is enough to have a single result to complete the project
            self._announce_results(storage)
            self.completed = True

    def _announce_results(self, storage):
        key = list(storage.values())[0][0]
        print('The cracked hash key is: {}'.format(key))
