import pyiec61850 as iec61850

SERVER_IP = "192.168.0.215"
SERVER_PORT = 102


def download_file(con, remote_name, local_name=None) -> bool:
    fp = None

    if local_name is None:
        local_name = remote_name.replace('/', '_')

    try:
        fp = iec61850.openFile(local_name)
        download_handler = iec61850.getIedconnectionDownloadHandler()
        readBytes, error = iec61850.IedConnection_getFile(con, remote_name, download_handler, fp)

        if error != iec61850.IED_ERROR_OK:
            print(f"Failed to download {remote_name}: error {error}")
            return False

        print(f"Successfully downloaded {remote_name} ({readBytes} bytes)")
        return True

    except Exception as e:
        print(f"Exception while downloading {remote_name}: {str(e)}")
        return False
    finally:
        if fp is not None:
            iec61850.closeFile(fp)


def main():
    con = None
    try:
        # Create and connect
        con = iec61850.IedConnection_create()
        error = iec61850.IedConnection_connect(con, SERVER_IP, SERVER_PORT)
        if error != iec61850.IED_ERROR_OK:
            print(f"Connection error: {error}")
            return

        # Get file list
        rootdir, error = iec61850.IedConnection_getFileDirectory(con, '/')
        if error != iec61850.IED_ERROR_OK:
            print(f"Failed to get directory: {error}")
            return

        # Process files
        filename_list = []
        direcEntry = iec61850.LinkedList_getNext(rootdir)

        while direcEntry:
            entry = iec61850.toFileDirectoryEntry(direcEntry.data)
            filename = iec61850.FileDirectoryEntry_getFileName(entry)
            filesize = iec61850.FileDirectoryEntry_getFileSize(entry)
            print(f"Found: {filename} ({filesize} bytes)")
            filename_list.append(filename)
            direcEntry = iec61850.LinkedList_getNext(direcEntry)

        # Download files
        for filename in filename_list:
            if filename.lower().endswith(('.dat', '.cfg')):  # Filter by extension if needed
                download_file(con, filename)

    finally:
        if con is not None:
            iec61850.IedConnection_close(con)
            iec61850.IedConnection_destroy(con)


if __name__ == "__main__":
    main()
