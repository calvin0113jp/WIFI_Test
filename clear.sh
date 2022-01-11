#!/bin/bash
echo -e "Removed the fw file and release note"

rm -f /tftpboot/downgrade/*
rm -f /tftpboot/upgrade/*
rm -f /tftpboot/releasenote/*

rm -f /tftpboot/web_dlink/upgrade/*
rm -f /tftpboot/web_dlink/downgrade/*

rm -f /tftpboot/dba/upgrade/*

echo -e "Please copy the file into thease folder before you testing"

echo -e "Put the new firmware into /tftpboot/downgrade"

echo -e "Put the old firmware into /tftpboot/upgrade/"

echo -e "Put the release note into /tftpboot/releasenote/"
