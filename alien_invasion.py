import sys
import pygame
from time import sleep, time
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button

GREY_COLOR = (128, 128, 128)
GREEN_COLOR = (0, 135, 0)


class AlienInvasion:
    def __init__(self) -> None:
        pygame.init()

        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        # Create an instance to store game statistics
        self.stats = GameStats(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()

        self.aliens = pygame.sprite.Group()
        self._create_fleet()

        # Active state
        self.game_active = False

        # Make the Play button
        self.play_button = Button(self, "Play")

        # Make the level button
        self.level = 1
        self.easy_button = Button(self, "Easy", button_color=GREY_COLOR)
        self.normal_button = Button(self, "Normal", button_color=GREEN_COLOR)
        self.hard_button = Button(self, "Hard", button_color=GREY_COLOR)

        self.easy_button.set_position(self.easy_button.rect.x - 2 * self.play_button.width,
                                      self.easy_button.rect.y + 2 * self.play_button.height)
        self.normal_button.set_position(self.play_button.rect.x,
                                        self.normal_button.rect.y + 2 * self.play_button.height)
        self.hard_button.set_position(self.hard_button.rect.x + 2 * self.play_button.width,
                                      self.hard_button.rect.y + 2 * self.play_button.height)

        # Make time increase speed button
        self.time_increase_speed_button = Button(
            self, "TimeLevel", button_color=GREY_COLOR)
        self.time_increase_speed_button.set_position(self.settings.screen_width - 2 * self.time_increase_speed_button.width,
                                                     self.time_increase_speed_button.height)

    def _check_events(self):
        """Respond to keypresses and mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_key_down_events(event)
            elif event.type == pygame.KEYUP:
                self._check_key_up_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                self._check_level_button(mouse_pos)
                self._check_time_increase_speed_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        '''Start a new game when the player clicks Play'''
        botton_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if botton_clicked and not self.game_active:
            self._start_game()

    def _check_level_button(self, mouse_pos):
        '''Set the level of the game'''
        easy_botton_clicked = self.easy_button.rect.collidepoint(mouse_pos)
        normal_botton_clicked = self.normal_button.rect.collidepoint(mouse_pos)
        hard_botton_clicked = self.hard_button.rect.collidepoint(mouse_pos)
        if easy_botton_clicked and not self.game_active:
            self.level = 0.7
            self.easy_button.set_color(GREEN_COLOR)
            self.normal_button.set_color(GREY_COLOR)
            self.hard_button.set_color(GREY_COLOR)
        elif normal_botton_clicked and not self.game_active:
            self.level = 1.0
            self.easy_button.set_color(GREY_COLOR)
            self.normal_button.set_color(GREEN_COLOR)
            self.hard_button.set_color(GREY_COLOR)
        elif hard_botton_clicked and not self.game_active:
            self.level = 2.0
            self.easy_button.set_color(GREY_COLOR)
            self.normal_button.set_color(GREY_COLOR)
            self.hard_button.set_color(GREEN_COLOR)

    def _check_time_increase_speed_button(self, mouse_pos):
        '''Set the level of the game'''
        time_increase_speed_botton_clicked = self.time_increase_speed_button.rect.collidepoint(
            mouse_pos)
        if time_increase_speed_botton_clicked and not self.game_active:
            self.settings.time_increase_speed = not self.settings.time_increase_speed
            if self.settings.time_increase_speed:
                self.time_increase_speed_button.set_color(GREEN_COLOR)
            else:
                self.time_increase_speed_button.set_color(GREY_COLOR)

    def _start_game(self):
        '''Start the game'''
        # Reset Stats
        self.stats.reset_stats()
        self.game_active = True

        self._reset_game()

        # Hide the mouse cursor
        pygame.mouse.set_visible(False)

        self.last_time = time()

    def _check_key_down_events(self, event):
        '''Respond to keypresses'''
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p and not self.game_active:
            self._start_game()

    def _check_key_up_events(self, event):
        '''Respond to key releases'''
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        '''Create a new bullet and add it to the bullets group'''
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        '''Update position of bullets and get rid of old bullets'''
        # Update bullet positions
        self.bullets.update()

        # Remove bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        # print(len(self.bullets))

        # Check for any bullets that have hit aliens
        # If so, get rid of the bullet and the alien
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions"""
        # Remove any bullets and aliens that have collided
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        if not self.aliens:
            # Destroy existing bullets and create new fleet
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the row"""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _create_fleet(self):
        """Create the fleet of aliens"""
        # Create an alien and find the number of aliens in a row
        # Spacing between each alien is equal to one alien width
        # Space from the top of the screen to the first alien is equal to
        # one alien height
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            # Move to the next row
            current_x = alien_width
            current_y += 2 * alien_height

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_aliens_bottom(self):
        '''Check if any aliens have reached the bottom of the screen'''
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.screen.get_rect().bottom:
                # Treat this the same as if the ship got hit
                self._ship_hit()
                break

    def _update_aliens(self):
        """Update the positions of all aliens in the fleet"""
        self._check_fleet_edges()
        self.aliens.update()

        # Check the collisions between aliens and the ship
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        self._check_aliens_bottom()

    def _ship_hit(self):
        '''Respond to the ship being hit by an alien'''
        if self.stats.ships_left > 0:
            # Decrement ships_left
            self.stats.ships_left -= 1

            self._reset_game()

            # Pause
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _reset_game(self):
        '''Reset the game'''
        self.settings.initialize_dynamic_settings(self.level)

        # Empty the list of aliens and bullets
        self.aliens.empty()
        self.bullets.empty()

        # Create a new fleet and center the ship
        self._create_fleet()
        self.ship.center_ship()

    def _update_time_increase_speed(self):
        '''Increase the speed of the game'''
        current_time = time()
        if current_time - self.last_time >= self.settings.time_interval:  # 检查是否达到30秒
            if self.settings.time_increase_speed:
                self.settings.increase_speed()
            self.last_time = current_time  # 重置计时器

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen"""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.ship.blitme()

        self.aliens.draw(self.screen)

        if not self.game_active:
            self.play_button.draw_button()
            self.easy_button.draw_button()
            self.normal_button.draw_button()
            self.hard_button.draw_button()
            self.time_increase_speed_button.draw_button()

        # Make the most recently drawn screen visible
        pygame.display.flip()

    def run_game(self):
        """start the main loop for the game"""
        while True:
            print(self.settings.alien_speed)

            # watch for keyboard and mouse events
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_time_increase_speed()

            self._update_screen()
            self.clock.tick(60)


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
