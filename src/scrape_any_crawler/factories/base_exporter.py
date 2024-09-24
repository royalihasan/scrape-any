from scrapy.exporters import BaseItemExporter
import json


class BaseExporter:
    def configure_export(settings):
        raise NotImplementedError(
            "You must implement the configure_export method")


class JSONExporter(BaseExporter):
    def configure_export(settings):
        settings['FEEDS'] = {
            'src/dumps/data/%(name)s/%(name)s/%(time)s.json': {'format': 'json'}

        }


class CSVExporter(BaseExporter):
    def configure_export(self, settings):
        settings['FEEDS'] = {
            'output.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'store_empty': False,
            },
        }


# class InMemoryJSONExporter(BaseExporter):
#     def __init__(self):
#         self.output = BytesIO()  # Use BytesIO for binary mode
#         self.exporter = JsonItemExporter(
#             self.output, ensure_ascii=False, indent=4)
#         self.exporter.start_exporting()

#     def process_item(self, item):
#         self.exporter.export_item(item)

#     def finish_exporting(self):
#         self.exporter.finish_exporting()

#     def get_data(self):
#         return self.output.getvalue().decode('utf-8')  # Decode bytes to string

#     def configure_export(self, settings):
#         # Here you can add custom settings or configurations if needed
#         pass


class InMemoryJSONExporter(BaseItemExporter):
    def __init__(self, *args, **kwargs):
        super(InMemoryJSONExporter, self).__init__(*args, **kwargs)
        self._buffer = []

    def finish_exporting(self):
        # Close the JSON array
        if self._buffer:
            self._buffer[-1] += b']'  # Close the array
        else:
            self._buffer = [b'[]']

    def export_item(self, item):
        # Convert item to JSON and ensure it's bytes
        item_data = json.dumps(item, ensure_ascii=False).encode('utf-8')
        self._buffer.append(item_data)

    def get_data(self):
        # Join buffer and return as a string
        return b'\n'.join(self._buffer).decode('utf-8')


# class InMemoryJSONPipeline:
#     def __init__(self, exporter):
#         self.exporter = exporter

#     def process_item(self, item, spider):
#         self.exporter.export_item(item)
#         return item

#     def close_spider(self, spider):
#         # When the spider closes, finalize the exporting
#         self.exporter.finish_exporting()


def create_pipeline():
    exporter = InMemoryJSONExporter()
    pipeline = InMemoryJSONPipeline(exporter)
    return pipeline, exporter
