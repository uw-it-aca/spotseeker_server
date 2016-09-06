from spotseeker_server.test import SpotServerTestCase


class ImageTestCase(SpotServerTestCase):

    def upload_image(self, image_file_name, url, extra_args=None):

        c = self.client
        with open(image_file_name) as f:
            res_args = {'image': f}
            if extra_args:
                res_args.update(extra_args)
            response = c.post(url, res_args)

        return response
