def original_query(level_ones, max_elements):
    str_query = ''
    nb_elements = 0
    separator = ''
    for levelOne in level_ones:
        if nb_elements >= max_elements:
            break
        str_query += separator
        str_query += levelOne
        separator = 'OR'
        nb_elements += 1

    print "==============================="
    print 'REGULAR QUERY (' + str(max_elements) + ")"
    print "==============================="
    print str_query
    print ""


def factorize_query(level_ones, max_elements):
    parts = []
    classification_level1 = []
    classification_level2 = []
    classification_level3 = []
    others = []

    nb_elements = 0
    for levelOne in level_ones:
        if nb_elements >= max_elements:
            break
        if "AND" in levelOne:
            if "(1)" in levelOne:
                level_two = levelOne.split('AND')
                # print "classif: " + level_two[0][2:]
                # print "root_cote: " + level_two[1][:-2]
                root_cote = level_two[1][:-2]
                classification_level1.append(root_cote.lstrip(' '))
            elif "(2)" in levelOne:
                level_two = levelOne.split('AND')
                # print "classif: " + level_two[0][2:]
                # print "root_cote: " + level_two[1][:-2]
                root_cote = level_two[1][:-2]
                classification_level2.append(root_cote.lstrip(' '))
            elif "(3)" in levelOne:
                level_two = levelOne.split('AND')
                # print "classif: " + level_two[0][2:]
                # print "root_cote: " + level_two[1][:-2]
                root_cote = level_two[1][:-2]
                classification_level3.append(root_cote.lstrip(' '))
        else:
            others.append(levelOne)
        nb_elements += 1

    parts.append(classification_level1)
    parts.append(classification_level2)
    parts.append(classification_level3)
    # print parts
    # print others

    separator = ''
    str_query = ''
    str_query += '('
    str_query += 'classification>=(1) AND '
    str_query += '('
    for root_cote in classification_level1:
        str_query += separator
        str_query += root_cote
        separator = ' OR '
    str_query += '))'

    str_query += ' OR '

    separator = ''
    str_query += '('
    str_query += 'classification>=(2) AND '
    str_query += '('
    for root_cote in classification_level2:
        str_query += separator
        str_query += root_cote
        separator = ' OR '
    str_query += '))'

    if len(classification_level3) > 0:
        separator = ''
        str_query += '('
        str_query += 'classification>=(3) AND '
        str_query += '('
        for root_cote in classification_level3:
            str_query += separator
            str_query += root_cote
            separator = ' OR '
        str_query += '))'

    if len(others) > 0:
        str_query += ' OR '
        str_query += others[0]
        str_query += ' OR '
        str_query += others[1]

    print "==============================="
    print 'FACTORIZED (' + str(max_elements) + ")"
    print "==============================="
    print str_query
    print ""


def factorize_expand_query(level_ones, max_elements):
    parts = []
    classification_level1 = []
    classification_level2 = []
    classification_level3 = []
    others = []

    nb_elements = 0
    for levelOne in level_ones:
        if nb_elements >= max_elements:
            break
        if "AND" in levelOne:
            if "(1)" in levelOne:
                level_two = levelOne.split('AND')
                # print "classif: " + level_two[0][2:]
                # print "root_cote: " + level_two[1][:-2]
                root_cote = level_two[1][:-2]
                classification_level1.append(root_cote.lstrip(' '))
                classification_level2.append(root_cote.lstrip(' '))
            elif "(2)" in levelOne:
                level_two = levelOne.split('AND')
                # print "classif: " + level_two[0][2:]
                # print "root_cote: " + level_two[1][:-2]
                root_cote = level_two[1][:-2]
                classification_level2.append(root_cote.lstrip(' '))
            elif "(3)" in levelOne:
                level_two = levelOne.split('AND')
                # print "classif: " + level_two[0][2:]
                # print "root_cote: " + level_two[1][:-2]
                root_cote = level_two[1][:-2]
                classification_level3.append(root_cote.lstrip(' '))
        else:
            others.append(levelOne)
        nb_elements += 1

    parts.append(classification_level1)
    parts.append(classification_level2)
    parts.append(classification_level3)
    # print parts
    # print others

    separator = ''
    str_query = ''
    str_query += '('
    str_query += 'classification=1 AND '
    str_query += '('
    for root_cote in classification_level1:
        str_query += separator
        str_query += root_cote
        separator = ' OR '
    str_query += '))'

    str_query += ' OR '

    separator = ''
    str_query += '('
    str_query += 'classification=2 AND '
    str_query += '('
    for root_cote in classification_level2:
        str_query += separator
        str_query += root_cote
        separator = ' OR '
    str_query += '))'

    if len(others) > 0:
        str_query += ' OR '
        str_query += others[0]
        str_query += ' OR '
        str_query += others[1]

    print "==============================="
    print 'FACTORIZED EXPANDED (' + str(max_elements) + ")"
    print "==============================="
    print str_query
    print ""


def no_classification_query(level_ones, max_elements):
    parts = []
    classification_level1 = []
    classification_level2 = []
    classification_level3 = []
    others = []

    nb_elements = 0
    for levelOne in level_ones:
        if nb_elements >= max_elements:
            break
        if "AND" in levelOne:
            if "(1)" in levelOne:
                level_two = levelOne.split('AND')
                # print "classif: " + level_two[0][2:]
                # print "root_cote: " + level_two[1][:-2]
                root_cote = level_two[1][:-2]
                classification_level1.append(root_cote.lstrip(' '))
            elif "(2)" in levelOne:
                level_two = levelOne.split('AND')
                # print "classif: " + level_two[0][2:]
                # print "root_cote: " + level_two[1][:-2]
                root_cote = level_two[1][:-2]
                classification_level2.append(root_cote.lstrip(' '))
            elif "(3)" in levelOne:
                level_two = levelOne.split('AND')
                # print "classif: " + level_two[0][2:]
                # print "root_cote: " + level_two[1][:-2]
                root_cote = level_two[1][:-2]
                classification_level3.append(root_cote.lstrip(' '))
        else:
            others.append(levelOne)
        nb_elements += 1

    parts.append(classification_level1)
    parts.append(classification_level2)
    parts.append(classification_level3)
    # print parts
    # print others

    separator = ''
    str_query = ''
    str_query += '('
    for root_cote in classification_level1:
        str_query += separator
        str_query += root_cote
        separator = ' OR '

    for root_cote in classification_level2:
        str_query += separator
        str_query += root_cote
        separator = ' OR '

    if len(classification_level3) > 0:
        for root_cote in classification_level3:
            str_query += separator
            str_query += root_cote
            separator = ' OR '
    str_query += ')'

    if len(others) > 0:
        str_query += ' OR '
        str_query += others[0]
        str_query += ' OR '
        str_query += others[1]

    print "==============================="
    print 'NO CLASSIFICATION (' + str(max_elements) + ")"
    print "==============================="
    print str_query


def main():
    level_ones = []

    with open("Olis_Query.txt") as queryFile:
        for line in queryFile:
            level_ones = line.split("OR")
        print "Found " + str(len(level_ones)) + " parts"

    max_parts = 460
    print "Maximum number of elements: " + str(max_parts)
    original_query(level_ones, max_parts)
    factorize_query(level_ones, max_parts)
    factorize_expand_query(level_ones, max_parts)
    no_classification_query(level_ones, max_parts)
    return

if __name__ == '__main__':
    main()
