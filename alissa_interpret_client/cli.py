import argparse

from alissa_interpret_client.alissa_interpret import AlissaInterpret


def upload_vcf(args):
    """Upload vcf file function."""
    client = AlissaInterpret(
        base_uri=args.base_uri,
        client_id=args.client_id,
        client_secret=args.client_secret,
        username=args.username,
        password=args.password
    )
    upload_vcf = client.post_data_file(args.vcf_file, type='VCF_FILE')
    print(upload_vcf)


def main():
    """CLI entry point."""

    # Parse CLI arguments
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=lambda args: parser.print_help())
    subparser = parser.add_subparsers()

    alissa_connection_parser = argparse.ArgumentParser(add_help=False)
    alissa_connection_parser.add_argument('base_uri', help='Alissa API base uri')
    alissa_connection_parser.add_argument('client_id', help='Alissa API client id')
    alissa_connection_parser.add_argument('client_secret', help='Alissa API client secret')
    alissa_connection_parser.add_argument('username', help='Alissa API username')
    alissa_connection_parser.add_argument('password', help='Alissa API password')

    parser_upload_vcf = subparser.add_parser(
        'upload_vcf', parents=[alissa_connection_parser], help='Upload VCF to Alissa Interpret'
    )
    parser_upload_vcf.add_argument('vcf_file', type=str, help='VCF file path')
    parser_upload_vcf.set_defaults(func=upload_vcf)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
