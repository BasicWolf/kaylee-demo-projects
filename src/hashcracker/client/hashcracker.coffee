pj = kl.pj

pj.init = (app_config) ->
    pj.config = app_config
    kl.include(app_config.md5_script, kl.project_imported.trigger, kl.error)
    return

pj.process_task = (task) ->
    task_id = task.id
    hash = task.hash_to_crack
    salt = task.salt
    key_id_start = task_id * pj.config.hashes_per_task

    for i in [0..pj.config.hashes_per_task - 1]
        key_id = key_id_start + i
        key = hash_key_from_decimal_id(key_id)
        kl.log("#{key}#{salt}")
        if hash == CryptoJS.MD5("#{key}#{salt}").toString(CryptoJS.enc.Hex)
            kl.task_completed.trigger({'cracked_key' : key})
    kl.task_completed.trigger(kl.NO_SOLUTION)
    return

hash_key_from_decimal_id = (id) ->
    config = pj.config
    alphabet = config.alphabet
    len = alphabet.length;
    i = id
    ret = ''
    while i > 0
        ret = alphabet.charAt(i % len) + ret
        i = Math.floor(i / len)

    # pad with 'zeroes' if required
    if ret.length < config.key_length
        for i in [0..config.key_length - ret.length - 1]
            ret = alphabet[0] + ret
    return ret
