
def get_destination_table(destination_table):
    return "{}.{}.{}".format(destination_table['projectId'],destination_table['datasetId'],destination_table['tableId'] )