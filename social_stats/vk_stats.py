import requests
import datetime


class VKStats:
    def __init__(self, vk_api_key, group_id):
        # Проверяем, что ID группы - это число, и убираем возможный "-"
        self.vk_api_key = vk_api_key
        self.group_id = str(group_id).lstrip('-')
        self.api_version = '5.199'

    def _make_api_request(self, method, params):
        """Вспомогательный метод для выполнения запросов к VK API."""
        url = f'https://api.vk.com/method/{method}'

        # Добавляем обязательные параметры в каждый запрос
        params['access_token'] = self.vk_api_key
        params['v'] = self.api_version

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Проверка на HTTP ошибки (4xx или 5xx)
            data = response.json()

            if 'error' in data:
                error_msg = data['error']['error_msg']
                # Добавим контекст к ошибке
                raise Exception(f"VK API Error: {error_msg}")

            return data.get('response')

        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error while connecting to VK API: {e}")

    def get_followers(self):
        """Получает общее количество подписчиков в группе."""
        params = {'group_id': self.group_id}
        response = self._make_api_request('groups.getMembers', params)
        return response.get('count', 0) if response else 0

    def get_activity_stats(self, start_date_obj, end_date_obj):
        """
        Получает и суммирует статистику по активностям (лайки, комментарии, репосты)
        за указанный период, используя Unix timestamp.
        """
        # Конвертируем datetime объекты в целочисленный Unix timestamp
        start_unix_time = int(start_date_obj.timestamp())
        end_unix_time = int(end_date_obj.timestamp())

        # Используем новые параметры: timestamp_from и timestamp_to
        params = {
            'group_id': self.group_id,
            'timestamp_from': start_unix_time,
            'timestamp_to': end_unix_time
        }

        # API stats.get возвращает список объектов, по одному на каждый день
        daily_stats = self._make_api_request('stats.get', params)

        # Инициализируем счетчики
        total_likes = 0
        total_comments = 0
        total_shares = 0

        if not daily_stats:
            return {'likes': 0, 'comments': 0, 'shares': 0}

        # Суммируем данные за каждый день
        for day_data in daily_stats:
            activity = day_data.get('activity')
            if activity:
                total_likes += activity.get('likes', 0)
                total_comments += activity.get('comments', 0)
                total_shares += activity.get('copies', 0)  # В API VK репосты называются 'copies'

        return {
            'likes': total_likes,
            'comments': total_comments,
            'shares': total_shares
        }